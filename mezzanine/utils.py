
from htmlentitydefs import name2codepoint
import os
import re
import sys

from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from django import VERSION


def admin_url(model, url, object_id=None):
    """
    Returns the admin url for the given model and url name.
    """
    opts = model._meta
    url = "admin:%s_%s_%s" % (opts.app_label, opts.object_name.lower(), url)
    args = ()
    if object_id is not None:
        args = (object_id,)
    return reverse(url, args=args)


def base_concrete_model(abstract, instance):
    """
    Used in methods of abstract models to find the super-most concrete
    (non abstract) model in the inheritence chain that inherits from the
    given abstract model. This is so the methods in the abstract model can
    query data consistantly across the correct concrete model.

    Consider the following::

        class Abstract(models.Model)

            class Meta:
                abstract = True

            def concrete(self):
                return base_concrete_model(Abstract, self)

        class Super(Abstract):
            pass

        class Sub(Super):
            pass

        sub = Sub.objects.create()
        sub.concrete() # returns Super

    In actual Mezzanine usage, this allows methods in the ``Displayable`` and
    ``Orderable`` abstract models to access the ``Page`` instance when
    instances of custom content types, (eg: models that inherit from ``Page``)
    need to query the ``Page`` model to determine correct values for ``slug``
    and ``_order`` which are only relevant in the context of the ``Page``
    model and not the model of the custom content type.
    """
    for cls in reversed(instance.__class__.__mro__):
        if issubclass(cls, abstract) and not cls._meta.abstract:
            return cls
    return instance.__class__
    

def content_media_urls(*paths):
    """
    Prefix the list of paths with the ``CONTENT_MEDIA_URL`` setting for 
    internally hosted JS and CSS files.
    """
    from mezzanine.conf import settings
    media_url = settings.CONTENT_MEDIA_URL.strip("/")
    return ["/%s/%s" % (media_url, path) for path in paths]


def decode_html_entities(html):
    """
    Remove HTML entities from a string.
    Adapted from http://effbot.org/zone/re-sub.htm#unescape-html
    """
    def decode(m):
        html = m.group(0)
        if html[:2] == "&#":
            try:
                if html[:3] == "&#x":
                    return unichr(int(html[3:-1], 16))
                else:
                    return unichr(int(html[2:-1]))
            except ValueError:
                pass
        else:
            try:
                html = unichr(name2codepoint[html[1:-1]])
            except KeyError:
                pass
        return html
    return re.sub("&#?\w+;", decode, html.replace("&amp;", "&"))


def is_editable(obj, request):
    """
    Returns True if the object is editable for the request. First check for
    a custom ``editable`` handler on the object, otherwise use the logged
    in user and check change permissions for the object's model.
    """
    if hasattr(obj, "is_editable"):
        return obj.is_editable(request)
    else:
        perm = obj._meta.app_label + "." + obj._meta.get_change_permission()
        return request.user.is_authenticated() and request.user.has_perm(perm)


def paginate(objects, page_num, per_page, max_paging_links):
    """
    Return a paginated page for the given objects, giving it a custom
    ``visible_page_range`` attribute calculated from ``max_paging_links``.
    """
    paginator = Paginator(list(objects), per_page)
    try:
        page_num = int(page_num)
    except ValueError:
        page_num = 1
    try:
        objects = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
    page_range = objects.paginator.page_range
    if len(page_range) > max_paging_links:
        start = min(objects.paginator.num_pages - max_paging_links,
            max(0, objects.number - (max_paging_links / 2) - 1))
        page_range = page_range[start:start + max_paging_links]
    objects.visible_page_range = page_range
    return objects


def path_for_import(name):
    """
    Returns the directory path for the given package or module.
    """
    return os.path.dirname(os.path.abspath(import_module(name).__file__))


def set_dynamic_settings(s):
    """
    Called at the end of the project's settings module and is passed its 
    globals dict for updating with some final tweaks for settings that 
    generally aren't specified but can be given some better defaults based on 
    other settings that have been specified. Broken out into its own 
    function so that the code need not be replicated in the settings modules 
    of other project-based apps that leverage Mezzanine's settings module.
    """

    s["TEMPLATE_DEBUG"] = s["DEBUG"]
    
    # Set ADMIN_MEDIA_PREFIX for Grappelli.
    grappelli = s["PACKAGE_NAME_GRAPPELLI"] in s["INSTALLED_APPS"]
    if grappelli:
        s["ADMIN_MEDIA_PREFIX"] = "/media/admin/"
        # Adopted from django.core.management.commands.runserver
        # Easiest way so far to actually get all the media for Grappelli 
        # working with the dev server is to hard-code the host:port to 
        # ADMIN_MEDIA_PREFIX, so here we check for a custom host:port 
        # before doing this.
        if len(sys.argv) >= 2 and sys.argv[1] == "runserver":
            addrport = ""
            if len(sys.argv) > 2:
                addrport = sys.argv[2]
            if not addrport:
                addr, port = "", "8000"
            else:
                try:
                    addr, port = addrport.split(":")
                except ValueError:
                    addr, port = "", addrport
            if not addr:
                addr = "127.0.0.1"
            s["ADMIN_MEDIA_PREFIX"] = "http://%s:%s%s" % (addr, port, 
                                                  s["ADMIN_MEDIA_PREFIX"])

    # Some settings tweaks for different DB engines.
    backend_path = "django.db.backends."
    backend_shortnames = (
        "postgresql_psycopg2",
        "postgresql",
        "mysql",
        "sqlite3",
        "oracle",
    )
    for (key, db) in s["DATABASES"].items():
        if db["ENGINE"] in backend_shortnames:
            s["DATABASES"][key]["ENGINE"] = backend_path + db["ENGINE"]
        shortname = db["ENGINE"].split(".")[-1]
        if shortname == "sqlite3" and os.sep not in db["NAME"]:
            # If the Sqlite DB name doesn't contain a path, assume it's 
            # in the project directory and add the path to it.
            s["DATABASES"][key]["NAME"] = os.path.join(
                                     s.get("_project_path", ""), db["NAME"])
        elif shortname == "mysql":
            # Required MySQL collation for tests.
            s["DATABASES"][key]["TEST_COLLATION"] = "utf8_general_ci"
        elif shortname.startswith("postgresql") and not s.get("TIME_ZONE", 1):
            # Specifying a blank time zone to fall back to the system's 
            # time zone will break table creation in Postgres so remove it.
            del s["TIME_ZONE"]

    # If a theme is defined then add its template path to the template dirs.
    theme = s.get("THEME")
    if theme:
        theme_templates = os.path.join(path_for_import(theme), "templates")
        s["TEMPLATE_DIRS"] = [theme_templates] + list(s["TEMPLATE_DIRS"])
        
    # Remaning code is for Django 1.1 support.
    if VERSION >= (1, 2, 0):
        return
    # Add the dummy csrf_token template tag to builtins and remove 
    # Django's CsrfViewMiddleware.
    from django.template.loader import add_to_builtins
    add_to_builtins("mezzanine.core.templatetags.dummy_csrf")
    s["MIDDLEWARE_CLASSES"] = [mw for mw in s["MIDDLEWARE_CLASSES"] if 
                        mw != "django.middleware.csrf.CsrfViewMiddleware"]
    # Use the single DB settings.
    old_db_settings_mapping = {
        "ENGINE": "DATABASE_ENGINE",
        "HOST": "DATABASE_HOST",
        "NAME": "DATABASE_NAME",
        "OPTIONS": "DATABASE_OPTIONS",
        "PASSWORD": "DATABASE_PASSWORD",
        "PORT": "DATABASE_PORT",
        "USER": "DATABASE_USER",
        "TEST_CHARSET": "TEST_DATABASE_CHARSET",
        "TEST_COLLATION": "TEST_DATABASE_COLLATION",
        "TEST_NAME": "TEST_DATABASE_NAME",
    }
    for (new_name, old_name) in old_db_settings_mapping.items():
        value = s["DATABASES"]["default"].get(new_name)
        if value is not None:
            if new_name == "ENGINE" and value.startswith(backend_path):
                value = value.replace(backend_path, "", 1)
            s[old_name] = value
    
    # Revert to some old names.
    processors = list(s["TEMPLATE_CONTEXT_PROCESSORS"])
    for (i, processor) in enumerate(processors):
        if processor == "django.contrib.auth.context_processors.auth":
            processors[i] = "django.core.context_processors.auth"
    s["TEMPLATE_CONTEXT_PROCESSORS"] = processors
    loaders = list(s["TEMPLATE_LOADERS"])
    for (i, loader) in enumerate(loaders):
        if loader.startswith("django.") and loader.endswith(".Loader"):
            loaders[i] = loader.replace(".Loader", ".load_template_source", 1)
    s["TEMPLATE_LOADERS"] = loaders
