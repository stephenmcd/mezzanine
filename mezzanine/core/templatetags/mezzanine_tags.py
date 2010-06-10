
from urllib import urlopen, urlencode

from django import template
from django.conf import settings
from django.utils.simplejson import loads

from mezzanine import settings as mezzanine_settings


register = template.Library()


@register.simple_tag
def setting(setting_name):
    """
    Return a setting.
    """
    return getattr(mezzanine_settings, setting_name, 
        getattr(settings, setting_name, ""))

def register_as_tag(register):
    """
    Decorator that creates a tag with the format: {% func_name as var_name %}
    The decorated func returns the value that is given to var_name in the 
    template context.
    """
    def wrapper(func):
        def tag(parser, token):
            class TagNode(template.Node):
                def render(self, context):
                    parts = token.split_contents()
                    context[parts[-1]] = func(*parts[1:-2])
                    return ""
            return TagNode()
        for copy_attr in ("__dict__", "__doc__", "__name__"):
            setattr(tag, copy_attr, getattr(func, copy_attr))
        return register.tag(tag)
    return wrapper

def register_render_tag(register):
    """
    Decorator that creates a template tag using the given renderer as the 
    render function for the template tag node - the render function takes two 
    arguments - the template context and the tag token
    """
    def wrapper(renderer):
        def tag(parser, token):
            class TagNode(template.Node):
                def render(self, context):
                    return renderer(context, token)
            return TagNode()
        for copy_attr in ("__dict__", "__doc__", "__name__"):
            setattr(tag, copy_attr, getattr(renderer, copy_attr))
        return register.tag(tag)
    return wrapper

@register_render_tag(register)
def set_short_url_for(context, token):
    """
    Sets the ``short_url`` attribute of the given model using the bit.ly 
    credentials if they have been specified and saves it.
    """
    obj = context[token.split_contents()[1]]
    request = context["request"]
    if getattr(obj, "short_url") is None:
        obj.short_url = request.build_absolute_uri(request.path)
        args = {
            "login": getattr(mezzanine_settings, "BLOG_BITLY_USER"),
            "apiKey": getattr(mezzanine_settings, "BLOG_BITLY_KEY"),
            "longUrl": obj.short_url,
        }
        if args["login"] and args["apiKey"]:
            url = "http://api.bit.ly/v3/shorten?%s" % urlencode(args)
            response = loads(urlopen(url).read())
            if response["status_code"] == 200:
                obj.short_url = response["data"]["url"]
                obj.save()
    return ""

@register_render_tag(register)
def admin_reorder(context, token):
    """
    Called in admin/base_site.html template override and applies custom ordering 
    of apps/models defined by settings.ADMIN_REORDER
    """
    # sort key function - use index of item in order if exists, otherwise item
    sort = lambda order, item: (order.index(item), "") if item in order else (
        len(order), item) 
    if "app_list" in context:
        # sort the app list
        order = SortedDict(mezzanine_settings.ADMIN_REORDER)
        context["app_list"].sort(key=lambda app: sort(order.keys(), 
            app["app_url"][:-1]))
        for i, app in enumerate(context["app_list"]):
            # sort the model list for each app
            app_name = app["app_url"][:-1]
            if not app_name:
                app_name = context["request"].path.strip("/").split("/")[-1]
            model_order = [m.lower() for m in order.get(app_name, [])]
            context["app_list"][i]["models"].sort(key=lambda model: 
                sort(model_order, model["admin_url"].strip("/").split("/")[-1]))
    return ""

