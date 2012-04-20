
from __future__ import with_statement
import os
from urllib import urlopen, urlencode, unquote

from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Model
from django.template import (Context, Node, Template, TemplateSyntaxError,
                             TOKEN_BLOCK)
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.simplejson import loads
from django.utils.text import capfirst

from PIL import Image, ImageOps

from mezzanine.conf import settings
from mezzanine.core.fields import RichTextField
from mezzanine.core.forms import get_edit_form
from mezzanine.utils.html import decode_entities
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.views import is_editable
from mezzanine.utils.urls import admin_url
from mezzanine import template


register = template.Library()


@register.inclusion_tag("includes/form_fields.html", takes_context=True)
def fields_for(context, form):
    """
    Renders fields for a form.
    """
    context["form_for_fields"] = form
    return context


@register.filter
def is_installed(app_name):
    """
    Returns ``True`` if the given app name is in the
    ``INSTALLED_APPS`` setting.
    """
    from warnings import warn
    warn("The is_installed filter is deprecated. Please use the tag "
         "{% ifinstalled appname %}{% endifinstalled %}")
    return app_name in settings.INSTALLED_APPS


@register.tag
def ifinstalled(parser, token):
    """
    Old-style ``if`` tag that renders contents if the given app is
    installed. The main use case is:
    {% ifinstalled app_name %}
        {% include "app_name/template.html" %}
    {% endifinstalled %}
    so we need to manually pull out all tokens if the app isn't
    installed, since if we used a normal ``if``tag with a False arg,
    the include tag will still try and find the template to include.
    """
    try:
        tag, app = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError("ifinstalled should be in the form: "
                                  "{% ifinstalled app_name %}"
                                  "{% endifinstalled %}")

    end_tag = "end" + tag
    if app.strip("\"'") not in settings.INSTALLED_APPS:
        while True:
            token = parser.tokens.pop(0)
            if token.token_type == TOKEN_BLOCK and token.contents == end_tag:
                parser.tokens.insert(0, token)
                break
    nodelist = parser.parse((end_tag,))
    parser.delete_first_token()

    class IfInstalledNode(Node):
        def render(self, context):
            return nodelist.render(context)

    return IfInstalledNode()


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
            "login": context["settings"].BLOG_BITLY_USER,
            "apiKey": context["settings"].BLOG_BITLY_KEY,
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
    return strip_tags(decode_entities(parsed))


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


@register.simple_tag
def thumbnail(image_url, width, height):
    """
    Given the URL to an image, resizes the image using the given width and
    height on the first time it is requested, and returns the URL to the new
    resized image. if width or height are zero then original ratio is
    maintained.
    """
    if not image_url:
        return ""

    image_url = unquote(unicode(image_url))
    if image_url.startswith(settings.MEDIA_URL):
        image_url = image_url.replace(settings.MEDIA_URL, "", 1)
    image_dir, image_name = os.path.split(image_url)
    image_prefix, image_ext = os.path.splitext(image_name)
    filetype = {".png": "PNG", ".gif": "GIF"}.get(image_ext, "JPEG")
    thumb_name = "%s-%sx%s%s" % (image_prefix, width, height, image_ext)
    thumb_dir = os.path.join(settings.MEDIA_ROOT, image_dir,
                             settings.THUMBNAILS_DIR_NAME)
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)
    thumb_path = os.path.join(thumb_dir, thumb_name)
    thumb_url = "%s/%s/%s" % (os.path.dirname(image_url),
                              settings.THUMBNAILS_DIR_NAME, thumb_name)

    try:
        thumb_exists = os.path.exists(thumb_path)
    except UnicodeEncodeError:
        # The image that was saved to a filesystem with utf-8 support,
        # but somehow the locale has changed and the filesystem does not
        # support utf-8.
        from mezzanine.core.exceptions import FileSystemEncodingChanged
        raise FileSystemEncodingChanged()
    if thumb_exists:
        # Thumbnail exists, don't generate it.
        return thumb_url
    elif not default_storage.exists(image_url):
        # Requested image does not exist, just return its URL.
        return image_url

    image = Image.open(default_storage.open(image_url))
    width = int(width)
    height = int(height)

    # If already right size, don't do anything.
    if width == image.size[0] and height == image.size[1]:
        return image_url
    # Set dimensions.
    if width == 0:
        width = image.size[0] * height / image.size[1]
    elif height == 0:
        height = image.size[1] * width / image.size[0]
    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")
    try:
        image = ImageOps.fit(image, (width, height), Image.ANTIALIAS)
        image = image.save(thumb_path, filetype, quality=100)
        # Push a remote copy of the thumbnail if MEDIA_URL is
        # absolute.
        if "://" in settings.MEDIA_URL:
            with open(thumb_path, "r") as f:
                default_storage.save(thumb_url, File(f))
    except:
        return image_url
    return thumb_url


@register.inclusion_tag("includes/editable_loader.html", takes_context=True)
def editable_loader(context):
    """
    Set up the required JS/CSS for the in-line editing toolbar and controls.
    """
    t = get_template("includes/editable_toolbar.html")
    context["REDIRECT_FIELD_NAME"] = REDIRECT_FIELD_NAME
    context["toolbar"] = t.render(Context(context))
    context["richtext_media"] = RichTextField().formfield().widget.media
    return context


@register.filter
def richtext_filter(content):
    """
    This template filter takes a string value and passes it through the
    function specified by the RICHTEXT_FILTER setting.
    """
    if settings.RICHTEXT_FILTER:
        func = import_dotted_path(settings.RICHTEXT_FILTER)
    else:
        func = lambda s: s
    return func(content)


@register.to_end_tag
def editable(parsed, context, token):
    """
    Add the required HTML to the parsed content for in-line editing, such as
    the icon and edit form if the object is deemed to be editable - either it
    has an ``editable`` method which returns ``True``, or the logged in user
    has change permissions for the model.
    """
    def parse_field(field):
        field = field.split(".")
        obj = context[field.pop(0)]
        attr = field.pop()
        while field:
            obj = getattr(obj, field.pop(0))
        return obj, attr

    fields = [parse_field(f) for f in token.split_contents()[1:]]
    if fields:
        fields = [f for f in fields if len(f) == 2 and f[0] is fields[0][0]]
    if not parsed.strip():
        try:
            parsed = "".join([unicode(getattr(*field)) for field in fields])
        except AttributeError:
            pass
    if fields and "request" in context:
        obj = fields[0][0]
        if isinstance(obj, Model) and is_editable(obj, context["request"]):
            field_names = ",".join([f[1] for f in fields])
            context["form"] = get_edit_form(obj, field_names)
            context["original"] = parsed
            t = get_template("includes/editable_form.html")
            return t.render(Context(context))
    return parsed


@register.simple_tag
def try_url(url_name):
    """
    Mimics Django's ``url`` template tag but fails silently. Used for url
    names in admin templates as these won't resolve when admin tests are
    running.
    """
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        return ""
    return url


def admin_app_list(request):
    """
    Adopted from ``django.contrib.admin.sites.AdminSite.index``. Returns a
    list of lists of models grouped and ordered according to
    ``mezzanine.conf.ADMIN_MENU_ORDER``. Called from the
    ``admin_dropdown_menu`` template tag as well as the ``app_list``
    dashboard widget.
    """
    app_dict = {}
    menu_order = [(x[0], list(x[1])) for x in settings.ADMIN_MENU_ORDER]
    found_items = set()
    for (model, model_admin) in admin.site._registry.items():
        opts = model._meta
        in_menu = not hasattr(model_admin, "in_menu") or model_admin.in_menu()
        if in_menu and request.user.has_module_perms(opts.app_label):
            perms = model_admin.get_model_perms(request)
            admin_url_name = ""
            if perms["change"]:
                admin_url_name = "changelist"
            elif perms["add"]:
                admin_url_name = "add"
            if admin_url_name:
                model_label = "%s.%s" % (opts.app_label, opts.object_name)
                for (name, items) in menu_order:
                    try:
                        index = list(items).index(model_label)
                    except ValueError:
                        pass
                    else:
                        found_items.add(model_label)
                        app_title = name
                        break
                else:
                    index = None
                    app_title = opts.app_label
                model_dict = {
                    "index": index,
                    "perms": model_admin.get_model_perms(request),
                    "name": capfirst(model._meta.verbose_name_plural),
                    "admin_url": admin_url(model, admin_url_name),
                }
                app_title = app_title.title()
                if app_title in app_dict:
                    app_dict[app_title]["models"].append(model_dict)
                else:
                    try:
                        titles = [x[0] for x in settings.ADMIN_MENU_ORDER]
                        index = titles.index(app_title)
                    except ValueError:
                        index = None
                    app_dict[app_title] = {
                        "index": index,
                        "name": app_title,
                        "models": [model_dict],
                    }

    for (i, (name, items)) in enumerate(menu_order):
        name = unicode(name)
        for unfound_item in set(items) - found_items:
            if isinstance(unfound_item, (list, tuple)):
                item_name, item_url = unfound_item[0], try_url(unfound_item[1])
                if item_url:
                    if name not in app_dict:
                        app_dict[name] = {
                            "index": i,
                            "name": name,
                            "models": [],
                        }
                    app_dict[name]["models"].append({
                        "index": items.index(unfound_item),
                        "perms": {"custom": True},
                        "name": item_name,
                        "admin_url": item_url,
                    })

    app_list = app_dict.values()
    sort = lambda x: x["name"] if x["index"] is None else x["index"]
    for app in app_list:
        app["models"].sort(key=sort)
    app_list.sort(key=sort)
    return app_list


@register.inclusion_tag("admin/includes/dropdown_menu.html",
                        takes_context=True)
def admin_dropdown_menu(context):
    """
    Renders the app list for the admin dropdown menu navigation.
    """
    context["dropdown_menu_app_list"] = admin_app_list(context["request"])
    return context


@register.inclusion_tag("admin/includes/app_list.html", takes_context=True)
def app_list(context):
    """
    Renders the app list for the admin dashboard widget.
    """
    context["dashboard_app_list"] = admin_app_list(context["request"])
    return context


@register.inclusion_tag("admin/includes/recent_actions.html",
                        takes_context=True)
def recent_actions(context):
    """
    Renders the recent actions list for the admin dashboard widget.
    """
    return context


@register.render_tag
def dashboard_column(context, token):
    """
    Takes an index for retrieving the sequence of template tags from
    ``mezzanine.conf.DASHBOARD_TAGS`` to render into the admin dashboard.
    """
    column_index = int(token.split_contents()[1])
    output = []
    for tag in settings.DASHBOARD_TAGS[column_index]:
        t = Template("{%% load %s %%}{%% %s %%}" % tuple(tag.split(".")))
        output.append(t.render(Context(context)))
    return "".join(output)
