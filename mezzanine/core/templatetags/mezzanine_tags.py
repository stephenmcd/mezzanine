import os
from hashlib import md5

try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.storage import default_storage
from django.db.models import Model
from django.template import Template, TemplateSyntaxError
from django.template.base import TextNode, TokenType
from django.template.defaultfilters import escape
from django.template.defaulttags import IfNode
from django.template.loader import get_template
from django.urls import NoReverseMatch, resolve, reverse
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.safestring import SafeText, mark_safe
from django.utils.text import capfirst

from mezzanine import template
from mezzanine.conf import settings
from mezzanine.core.fields import RichTextField
from mezzanine.core.forms import get_edit_form
from mezzanine.utils.cache import cache_installed, nevercache_token
from mezzanine.utils.html import decode_entities
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.sites import current_site_id, has_site_permission
from mezzanine.utils.urls import admin_url, home_slug
from mezzanine.utils.views import is_editable

register = template.Library()


if "compressor" in settings.INSTALLED_APPS:

    @register.tag
    def compress(parser, token):
        """
        Shadows django-compressor's compress tag so it can be
        loaded from ``mezzanine_tags``, allowing us to provide
        a dummy version when django-compressor isn't installed.
        """
        from compressor.templatetags.compress import compress

        return compress(parser, token)


else:

    @register.to_end_tag
    def compress(parsed, context, token):
        """
        Dummy tag for fallback when django-compressor isn't installed.
        """
        return parsed


def initialize_nevercache():
    if cache_installed():

        @register.tag
        def nevercache(parser, token):
            """
            Tag for two phased rendering. Converts enclosed template
            code and content into text, which gets rendered separately
            in ``mezzanine.core.middleware.UpdateCacheMiddleware``.
            This is to bypass caching for the enclosed code and content.
            """
            text = []
            end_tag = "endnevercache"
            tag_mapping = {
                TokenType.TEXT: ("", ""),
                TokenType.VAR: ("{{", "}}"),
                TokenType.BLOCK: ("{%", "%}"),
                TokenType.COMMENT: ("{#", "#}"),
            }
            delimiter = nevercache_token()
            while parser.tokens:
                token = parser.next_token()
                token_type = token.token_type
                if token_type == TokenType.BLOCK and token.contents == end_tag:
                    return TextNode(delimiter + "".join(text) + delimiter)
                start, end = tag_mapping[token_type]
                text.append(f"{start}{token.contents}{end}")
            parser.unclosed_block_tag(end_tag)

    else:

        @register.to_end_tag
        def nevercache(parsed, context, token):
            """
            Dummy fallback ``nevercache`` for when caching is not
            configured.
            """
            return parsed


initialize_nevercache()


@register.simple_tag(takes_context=True)
def fields_for(context, form, template="includes/form_fields.html"):
    """
    Renders fields for a form with an optional template choice.
    """
    context["form_for_fields"] = form
    return get_template(template).render(context.flatten())


@register.inclusion_tag("includes/form_errors.html")
def errors_for(form):
    """
    Renders an alert if the form has any errors.
    """
    return {"form": form}


@register.filter
def sort_by(items, attr):
    """
    General sort filter - sorts by either attribute or key.
    """

    def key_func(item):
        try:
            return getattr(item, attr)
        except AttributeError:
            try:
                return item[attr]
            except TypeError:
                getattr(item, attr)  # Reraise AttributeError

    return sorted(items, key=key_func)


@register.filter
def is_installed(app_name):
    """
    Returns ``True`` if the given app name is in the
    ``INSTALLED_APPS`` setting.
    """
    from warnings import warn

    warn(
        "The is_installed filter is deprecated. Please use the tag "
        "{% ifinstalled appname %}{% endifinstalled %}"
    )
    return app_name in settings.INSTALLED_APPS


class EvalWrapper:
    def __init__(self, value):
        """Compatibility class for ``value`` to work with Django's ``IfNode``"""
        self.value = value

    def eval(self, context):
        return self.value


@register.tag
def ifinstalled(parser, token):
    """
    ``if`` tag that renders contents if the given app is installed. The main use case
    is:

    {% ifinstalled "app_name" %}
    {% include "app_name/template.html" %}
    {% endifinstalled %}
    """
    try:
        tag, app = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError(
            "ifinstalled should be in the form: "
            "{% ifinstalled app_name %}{% endifinstalled %}"
        )

    condition = app.strip("\"'") in settings.INSTALLED_APPS
    nodelist = parser.parse([f"end{tag}"])
    conditions_nodelists = [(EvalWrapper(condition), nodelist)]
    token = parser.next_token()
    return IfNode(conditions_nodelists)


@register.render_tag
def set_short_url_for(context, token):
    """
    Sets the ``short_url`` attribute of the given model for share
    links in the template.
    """
    obj = context[token.split_contents()[1]]
    obj.set_short_url()
    return ""


@register.simple_tag
def gravatar_url(email, size=32):
    """
    Return the full URL for a Gravatar given an email hash.
    """
    bits = (md5(email.lower().encode("utf-8")).hexdigest(), size)
    return "//www.gravatar.com/avatar/%s?s=%s&d=identicon&r=PG" % bits


@register.to_end_tag
def metablock(parsed):
    """
    Remove HTML tags, entities and superfluous characters from
    meta blocks.
    """
    parsed = " ".join(parsed.replace("\n", "").split()).replace(" ,", ",")
    return escape(strip_tags(decode_entities(parsed)))


@register.inclusion_tag("includes/pagination.html", takes_context=True)
def pagination_for(context, current_page, page_var="page", exclude_vars=""):
    """
    Include the pagination template and data for persisting querystring
    in pagination links. Can also contain a comma separated string of
    var names in the current querystring to exclude from the pagination
    links, via the ``exclude_vars`` arg.
    """
    querystring = context["request"].GET.copy()
    exclude_vars = [v for v in exclude_vars.split(",") if v] + [page_var]
    for exclude_var in exclude_vars:
        if exclude_var in querystring:
            del querystring[exclude_var]
    querystring = querystring.urlencode()
    return {
        "current_page": current_page,
        "querystring": querystring,
        "page_var": page_var,
    }


@register.inclusion_tag("includes/search_form.html", takes_context=True)
def search_form(context, search_model_names=None):
    """
    Includes the search form with a list of models to use as choices
    for filtering the search by. Models should be a string with models
    in the format ``app_label.model_name`` separated by spaces. The
    string ``all`` can also be used, in which case the models defined
    by the ``SEARCH_MODEL_CHOICES`` setting will be used.
    """
    template_vars = {
        "request": context["request"],
    }
    if not search_model_names or not settings.SEARCH_MODEL_CHOICES:
        search_model_names = []
    elif search_model_names == "all":
        search_model_names = list(settings.SEARCH_MODEL_CHOICES)
    else:
        search_model_names = search_model_names.split(" ")
    search_model_choices = []
    for model_name in search_model_names:
        try:
            model = apps.get_model(*model_name.split(".", 1))
        except LookupError:
            pass
        else:
            verbose_name = model._meta.verbose_name_plural.capitalize()
            search_model_choices.append((verbose_name, model_name))
    template_vars["search_model_choices"] = sorted(search_model_choices)
    return template_vars


@register.simple_tag
def thumbnail(
    image_url,
    width,
    height,
    upscale=True,
    quality=95,
    left=0.5,
    top=0.5,
    padding=False,
    padding_color="#fff",
):
    """
    Given the URL to an image, resizes the image using the given width
    and height on the first time it is requested, and returns the URL
    to the new resized image. If width or height are zero then original
    ratio is maintained. When ``upscale`` is False, images smaller than
    the given size will not be grown to fill that size. The given width
    and height thus act as maximum dimensions.
    """

    if not image_url:
        return ""
    try:
        from PIL import Image, ImageFile, ImageOps
    except ImportError:
        return ""

    image_url = unquote(str(image_url)).split("?")[0]
    if image_url.startswith(settings.MEDIA_URL):
        image_url = image_url.replace(settings.MEDIA_URL, "", 1)
    image_dir, image_name = os.path.split(image_url)
    image_prefix, image_ext = os.path.splitext(image_name)
    filetype = {".png": "PNG", ".gif": "GIF"}.get(image_ext.lower(), "JPEG")
    thumb_name = f"{image_prefix}-{width}x{height}"
    if not upscale:
        thumb_name += "-no-upscale"
    if left != 0.5 or top != 0.5:
        left = min(1, max(0, left))
        top = min(1, max(0, top))
        thumb_name = f"{thumb_name}-{left}x{top}"
    thumb_name += "-padded-%s" % padding_color if padding else ""
    thumb_name = f"{thumb_name}{image_ext}"

    # `image_name` is used here for the directory path, as each image
    # requires its own sub-directory using its own name - this is so
    # we can consistently delete all thumbnails for an individual
    # image, which is something we do in filebrowser when a new image
    # is written, allowing us to purge any previously generated
    # thumbnails that may match a new image name.
    thumb_dir = os.path.join(
        settings.MEDIA_ROOT, image_dir, settings.THUMBNAILS_DIR_NAME, image_name
    )
    if not os.path.exists(thumb_dir):
        try:
            os.makedirs(thumb_dir)
        except OSError:
            pass

    thumb_path = os.path.join(thumb_dir, thumb_name)
    thumb_url = "{}/{}/{}".format(
        settings.THUMBNAILS_DIR_NAME,
        quote(image_name.encode("utf-8")),
        quote(thumb_name.encode("utf-8")),
    )
    image_url_path = os.path.dirname(image_url)
    if image_url_path:
        thumb_url = f"{image_url_path}/{thumb_url}"

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

    f = default_storage.open(image_url)
    try:
        image = Image.open(f)
    except:  # noqa
        # Invalid image format.
        return image_url

    image_info = image.info

    # Transpose to align the image to its orientation if necessary.
    # If the image is transposed, delete the exif information as
    # not all browsers support the CSS image-orientation:
    # - http://caniuse.com/#feat=css-image-orientation
    try:
        orientation = image._getexif().get(0x0112)
    except:  # noqa
        orientation = None
    if orientation:
        methods = {
            2: (Image.FLIP_LEFT_RIGHT,),
            3: (Image.ROTATE_180,),
            4: (Image.FLIP_TOP_BOTTOM,),
            5: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_90),
            6: (Image.ROTATE_270,),
            7: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_270),
            8: (Image.ROTATE_90,),
        }.get(orientation, ())
        if methods:
            image_info.pop("exif", None)
            for method in methods:
                image = image.transpose(method)

    to_width = int(width)
    to_height = int(height)
    from_width = image.size[0]
    from_height = image.size[1]

    if not upscale:
        to_width = min(to_width, from_width)
        to_height = min(to_height, from_height)

    # Set dimensions.
    if to_width == 0:
        to_width = from_width * to_height // from_height
    elif to_height == 0:
        to_height = from_height * to_width // from_width
    if image.mode not in ("P", "L", "RGBA") and filetype not in ("JPG", "JPEG"):
        try:
            image = image.convert("RGBA")
        except:  # noqa
            return image_url
    # Required for progressive jpgs.
    ImageFile.MAXBLOCK = 2 * (max(image.size) ** 2)

    # Padding.
    if padding and to_width and to_height:
        from_ratio = float(from_width) / from_height
        to_ratio = float(to_width) / to_height
        pad_size = None
        if to_ratio < from_ratio:
            pad_height = int(to_height * (float(from_width) / to_width))
            pad_size = (from_width, pad_height)
            pad_top = (pad_height - from_height) // 2
            pad_left = 0
        elif to_ratio > from_ratio:
            pad_width = int(to_width * (float(from_height) / to_height))
            pad_size = (pad_width, from_height)
            pad_top = 0
            pad_left = (pad_width - from_width) // 2
        if pad_size is not None:
            pad_container = Image.new("RGBA", pad_size, padding_color)
            pad_container.paste(image, (pad_left, pad_top))
            image = pad_container

    # Create the thumbnail.
    to_size = (to_width, to_height)
    to_pos = (left, top)
    try:
        image = ImageOps.fit(image, to_size, Image.ANTIALIAS, 0, to_pos)
        image = image.save(thumb_path, filetype, quality=quality, **image_info)
        # Push a remote copy of the thumbnail if MEDIA_URL is
        # absolute.
        if "://" in settings.MEDIA_URL:
            with open(thumb_path, "rb") as f:
                default_storage.save(unquote(thumb_url), File(f))
    except Exception:
        # If an error occurred, a corrupted image may have been saved,
        # so remove it, otherwise the check for it existing will just
        # return the corrupted image next time it's requested.
        try:
            os.remove(thumb_path)
        except Exception:
            pass
        return image_url
    return thumb_url


@register.inclusion_tag("includes/editable_loader.html", takes_context=True)
def editable_loader(context):
    """
    Set up the required JS/CSS for the in-line editing toolbar and controls.
    """
    user = context["request"].user
    template_vars = {
        "has_site_permission": has_site_permission(user),
        "request": context["request"],
    }
    if settings.INLINE_EDITING_ENABLED and template_vars["has_site_permission"]:
        t = get_template("includes/editable_toolbar.html")
        template_vars["REDIRECT_FIELD_NAME"] = REDIRECT_FIELD_NAME
        template_vars["editable_obj"] = context.get(
            "editable_obj", context.get("page", None)
        )
        template_vars["accounts_logout_url"] = context.get("accounts_logout_url", None)
        template_vars["toolbar"] = t.render(template_vars)
        template_vars["richtext_media"] = RichTextField().formfield().widget.media
    return template_vars


@register.filter
def richtext_filters(content):
    """
    Takes a value edited via the WYSIWYG editor, and passes it through
    each of the functions specified by the RICHTEXT_FILTERS setting.
    """
    for filter_name in settings.RICHTEXT_FILTERS:
        filter_func = import_dotted_path(filter_name)
        content = filter_func(content)
        if not isinstance(content, SafeText):
            # raise TypeError(
            # filter_name + " must mark it's return value as safe. See "
            # "https://docs.djangoproject.com/en/stable/topics/security/"
            # "#cross-site-scripting-xss-protection")
            import warnings

            warnings.warn(
                filter_name + " needs to ensure that any untrusted inputs are "
                "properly escaped and mark the html it returns as safe. In a "
                "future release this will cause an exception. See "
                "https://docs.djangoproject.com/en/stable/topics/security/"
                "cross-site-scripting-xss-protection",
                FutureWarning,
            )
            content = mark_safe(content)
    return content


@register.to_end_tag
def editable(parsed, context, token):
    """
    Add the required HTML to the parsed content for in-line editing,
    such as the icon and edit form if the object is deemed to be
    editable - either it has an ``editable`` method which returns
    ``True``, or the logged in user has change permissions for the
    model.
    """

    def parse_field(field):
        field = field.split(".")
        obj = context.get(field.pop(0), None)
        attr = field.pop()
        while field:
            obj = getattr(obj, field.pop(0))
            if callable(obj):
                # Allows {% editable page.get_content_model.content %}
                obj = obj()
        return obj, attr

    fields = [parse_field(f) for f in token.split_contents()[1:]]
    if fields:
        fields = [f for f in fields if len(f) == 2 and f[0] is fields[0][0]]
    if not parsed.strip():
        try:
            parsed = "".join(str(getattr(*field)) for field in fields)
        except AttributeError:
            pass

    if settings.INLINE_EDITING_ENABLED and fields and "request" in context:
        obj = fields[0][0]
        if isinstance(obj, Model) and is_editable(obj, context["request"]):
            field_names = ",".join(f[1] for f in fields)
            context["editable_form"] = get_edit_form(obj, field_names)
            context["original"] = parsed
            t = get_template("includes/editable_form.html")
            return t.render(context.flatten())
    return parsed


@register.simple_tag
def try_url(url_name):
    """
    Mimics Django's ``url`` template tag but fails silently. Used for
    url names in admin templates as these won't resolve when admin
    tests are running.
    """
    from warnings import warn

    warn("try_url is deprecated, use the url tag with the 'as' arg instead.")
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        return ""
    return url


def admin_app_list(request):
    """
    Adopted from ``django.contrib.admin.sites.AdminSite.index``.
    Returns a list of lists of models grouped and ordered according to
    ``mezzanine.conf.ADMIN_MENU_ORDER``. Called from the
    ``admin_dropdown_menu`` template tag as well as the ``app_list``
    dashboard widget.
    """
    app_dict = {}

    # Model or view --> (group index, group title, item index, item title).
    menu_order = {}
    for (group_index, group) in enumerate(settings.ADMIN_MENU_ORDER):
        group_title, items = group
        for (item_index, item) in enumerate(items):
            if isinstance(item, (tuple, list)):
                item_title, item = item
            else:
                item_title = None
            menu_order[item] = (group_index, group_title, item_index, item_title)

    # Add all registered models, using group and title from menu order.
    for (model, model_admin) in admin.site._registry.items():
        opts = model._meta
        in_menu = not hasattr(model_admin, "in_menu") or model_admin.in_menu()
        if hasattr(model_admin, "in_menu"):
            import warnings

            warnings.warn(
                "ModelAdmin.in_menu() has been replaced with "
                "ModelAdmin.has_module_permission(request). See "
                "https://docs.djangoproject.com/en/stable/ref/contrib/admin/"
                "#django.contrib.admin.ModelAdmin.has_module_permission.",
                DeprecationWarning,
            )
        in_menu = in_menu and model_admin.has_module_permission(request)
        if in_menu and request.user.has_module_perms(opts.app_label):
            admin_url_name = ""
            if model_admin.has_change_permission(request):
                admin_url_name = "changelist"
                change_url = admin_url(model, admin_url_name)
            else:
                change_url = None
            if model_admin.has_add_permission(request):
                admin_url_name = "add"
                add_url = admin_url(model, admin_url_name)
            else:
                add_url = None
            if admin_url_name:
                model_label = f"{opts.app_label}.{opts.object_name}"
                try:
                    app_index, app_title, model_index, model_title = menu_order[
                        model_label
                    ]
                except KeyError:
                    app_index = None
                    try:
                        app_title = opts.app_config.verbose_name.title()
                    except AttributeError:
                        # Third party admin classes doing weird things.
                        # See GH #1628
                        app_title = ""
                    model_index = None
                    model_title = None
                else:
                    del menu_order[model_label]

                if not model_title:
                    model_title = capfirst(model._meta.verbose_name_plural)

                if app_title not in app_dict:
                    app_dict[app_title] = {
                        "index": app_index,
                        "name": app_title,
                        "models": [],
                    }
                app_dict[app_title]["models"].append(
                    {
                        "index": model_index,
                        "perms": model_admin.get_model_perms(request),
                        "name": model_title,
                        "object_name": opts.object_name,
                        "admin_url": change_url,
                        "add_url": add_url,
                    }
                )

    # Menu may also contain view or url pattern names given as (title, name).
    for (item_url, item) in menu_order.items():
        app_index, app_title, item_index, item_title = item
        try:
            item_url = reverse(item_url)
        except NoReverseMatch:
            continue
        if app_title not in app_dict:
            app_dict[app_title] = {
                "index": app_index,
                "name": app_title,
                "models": [],
            }
        app_dict[app_title]["models"].append(
            {
                "index": item_index,
                "perms": {"custom": True},
                "name": item_title,
                "admin_url": item_url,
            }
        )

    app_list = list(app_dict.values())
    sort = lambda x: (x["index"] if x["index"] is not None else 999, x["name"])
    for app in app_list:
        app["models"].sort(key=sort)
    app_list.sort(key=sort)
    return app_list


@register.inclusion_tag("admin/includes/dropdown_menu.html", takes_context=True)
def admin_dropdown_menu(context):
    """
    Renders the app list for the admin dropdown menu navigation.
    """
    user = context["request"].user
    if user.is_staff:
        context["dropdown_menu_app_list"] = admin_app_list(context["request"])
        if user.is_superuser:
            sites = Site.objects.all()
        else:
            try:
                sites = user.sitepermissions.sites.all()
            except ObjectDoesNotExist:
                sites = Site.objects.none()
        context["dropdown_menu_sites"] = list(sites)
        context["dropdown_menu_selected_site_id"] = current_site_id()
        return context.flatten()


@register.inclusion_tag("admin/includes/app_list.html", takes_context=True)
def app_list(context):
    """
    Renders the app list for the admin dashboard widget.
    """
    context["dashboard_app_list"] = admin_app_list(context["request"])
    return context.flatten()


@register.inclusion_tag("admin/includes/recent_actions.html", takes_context=True)
def recent_actions(context):
    """
    Renders the recent actions list for the admin dashboard widget.
    """
    return context.flatten()


@register.render_tag
def dashboard_column(context, token):
    """
    Takes an index for retrieving the sequence of template tags from
    ``mezzanine.conf.DASHBOARD_TAGS`` to render into the admin
    dashboard.
    """
    column_index = int(token.split_contents()[1])
    output = []
    for tag in settings.DASHBOARD_TAGS[column_index]:
        t = Template("{%% load %s %%}{%% %s %%}" % tuple(tag.split(".")))
        output.append(t.render(context))
    return "".join(output)


@register.simple_tag(takes_context=True)
def translate_url(context, language):
    """
    Translates the current URL for the given language code, eg:

        {% translate_url "de" %}
    """
    try:
        request = context["request"]
    except KeyError:
        return ""
    view = resolve(request.path)
    current_language = translation.get_language()
    translation.activate(language)
    if not view.namespace and view.url_name == "home":
        url = home_slug()
    else:
        try:
            url = reverse(view.func, args=view.args, kwargs=view.kwargs)
        except NoReverseMatch:
            try:
                url_name = (
                    view.url_name
                    if not view.namespace
                    else f"{view.namespace}:{view.url_name}"
                )
                url = reverse(url_name, args=view.args, kwargs=view.kwargs)
            except NoReverseMatch:
                url_name = "admin:" + view.url_name
                url = reverse(url_name, args=view.args, kwargs=view.kwargs)
    translation.activate(current_language)
    qs = context["request"].META.get("QUERY_STRING", "")
    if qs:
        url += "?" + qs
    return url
