
from urllib import urlopen, urlencode
from uuid import uuid4

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.db.models import Model
from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.simplejson import loads
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from mezzanine import settings as mezzanine_settings
from mezzanine import template
from mezzanine.core.forms import get_edit_form
from mezzanine.utils import decode_html_entities, is_editable


register = template.Library()


@register.simple_tag
def setting(setting_name, called_internally=False):
    """
    Return a setting.
    """
    if not called_internally:
        import warnings
        warnings.warn(
            "The ``setting`` tag will be deprecated - " \
            "please use the ``load_settings`` tag.", DeprecationWarning)
    value = getattr(mezzanine_settings, setting_name,
        getattr(settings, setting_name, None))
    if value is None:
        value = ""
    return value


@register.render_tag
def load_settings(context, token):
    """
    Push the given setting names into the context.
    """
    for setting_name in token.split_contents()[1:]:
        context[setting_name] = setting(setting_name, called_internally=True)
    return ""


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
    Add the required HTML to the parsed content for in-line editing, such as
    the icon and edit form if the object is deemed to be editable - either it
    has an ``editable`` method which returns True, or the logged in user has
    change permissions for the model.
    """
    parts = token.split_contents()[1].split(".")
    obj = context[parts.pop(0)]
    attr = parts.pop()
    while parts:
        obj = getattr(obj, parts.pop(0))
    if not parsed.strip():
        parsed = getattr(obj, attr)
    if isinstance(obj, Model) and is_editable(obj, context["request"]):
        context["form"] = get_edit_form(obj, attr)
        context["original"] = parsed
        context["uuid"] = uuid4()
        t = get_template("includes/editable_form.html")
        return t.render(Context(context))
    return parsed


@register.inclusion_tag("admin/includes/dropdown_menu.html", takes_context=True)
def admin_dropdown_menu(context):
    """
    Adopted from ``django.contrib.admin.sites.AdminSite.index``. Renders a 
    list of lists of models grouped and ordered according to 
    ``mezzanine.settings.ADMIN_MENU_ORDER``.
    """
    app_dict = {}
    user = context["request"].user
    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label
        in_menu = not hasattr(model_admin, "in_menu") or model_admin.in_menu()
        if in_menu and user.has_module_perms(app_label):
            perms = model_admin.get_model_perms(context["request"])
            admin_url = ""
            if perms["change"]:
                admin_url = "changelist"
            elif perms["add"]:
                admin_url = "add"
            if admin_url:
                model_label = "%s.%s" % (app_label, model.__name__)
                for (name, items) in mezzanine_settings.ADMIN_MENU_ORDER:
                    try:
                        index = items.index(model_label)
                    except ValueError:
                        pass
                    else:
                        app_title = name
                        break
                else:
                    index = None
                    app_title = app_label
                model_dict = {
                    "index": index,
                    "name": capfirst(model._meta.verbose_name_plural),
                    "admin_url": reverse("admin:%s_%s_%s" % (
                        app_label, model.__name__.lower(), admin_url))
                }
                app_title = app_title.title()
                if app_title in app_dict:
                    app_dict[app_title]["models"].append(model_dict)
                else:
                    try:
                        titles = [x[0] for x in 
                            mezzanine_settings.ADMIN_MENU_ORDER]
                        index = titles.index(app_title)
                    except ValueError:
                        index = None
                    app_dict[app_title] = {
                        "index": index,
                        "name": app_title,
                        "models": [model_dict],
                    }
    app_list = app_dict.values()
    sort = lambda x: x["name"] if x["index"] is None else x["index"]
    for app in app_list:
        app["models"].sort(key=sort)
    app_list.sort(key=sort)
    return {"app_list": app_list}

