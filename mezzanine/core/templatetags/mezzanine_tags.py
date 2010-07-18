
from urllib import urlopen, urlencode
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db.models import Model
from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.simplejson import loads

from mezzanine import settings as mezzanine_settings
from mezzanine import template
from mezzanine.core.forms import get_edit_form
from mezzanine.utils import decode_html_entities


register = template.Library()


@register.simple_tag
def setting(setting_name):
    """
    Return a setting.
    """
    value = getattr(mezzanine_settings, setting_name, 
        getattr(settings, setting_name, None))
    if value is None:
        value = ""
    return value

@register.render_tag
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

@register.render_tag
def admin_reorder(context, token):
    """
    Called in ``admin/base_site.html`` template override and applies custom 
    ordering of apps/models defined by ``settings.ADMIN_REORDER``.
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

@register.to_end_tag
def metablock(parsed):
    """
    Remove HTML tags, entities and superfluous characters from meta blocks.
    """
    parsed = " ".join(parsed.replace("\n", "").split()).replace(" ,", ",")
    return strip_tags(decode_html_entities(parsed))

@register.inclusion_tag("includes/pagination.html", takes_context=True)
def pagination_for(context, current_page):
    """
    Include the pagination template and data for persisting querystring in 
    pagination links.
    """
    querystring = context["request"].GET.copy()
    if "page" in querystring:
        del querystring["page"]
    querystring = querystring.urlencode()
    return {"current_page": current_page, "querystring": querystring}

@register.inclusion_tag("includes/editable_loader.html", takes_context=True)
def editable_loader(context):
    """
    Set up the required JS/CSS for the in-line editing toolbar and controls.
    """
    t = get_template("includes/editable_toolbar.html") 
    context["REDIRECT_FIELD_NAME"] = REDIRECT_FIELD_NAME
    context["toolbar"] = t.render(Context(context))
    return context

@register.to_end_tag
def editable(parsed, context, token):
    """
    If the user is staff, add the required HTML to the parsed content for 
    in-line editing such as the icon and edit form.
    """
    var, attr = token.split_contents()[1].split(".")
    obj = context[var]
    if not parsed.strip():
        parsed = getattr(obj, attr)
    user = context["request"].user
    if isinstance(obj, Model) and user.is_staff:
        perm = obj._meta.app_label + "." + obj._meta.get_change_permission()
        if user.has_perm(perm):
            context["form"] = get_edit_form(obj, attr)
            context["original"] = parsed
            context["uuid"] = uuid4()
            t = get_template("includes/editable_form.html") 
            return t.render(Context(context))
    return parsed

