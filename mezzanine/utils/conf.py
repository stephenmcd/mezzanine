
import os
import sys

from django.template.loader import add_to_builtins
from django import VERSION

from mezzanine.utils.path import path_for_import


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
    add_to_builtins("mezzanine.template.loader_tags")

    # Setup for optional apps.
    if "debug_toolbar" in s["INSTALLED_APPS"]:
        debug_mw = "debug_toolbar.middleware.DebugToolbarMiddleware"
        if debug_mw not in s["MIDDLEWARE_CLASSES"]:
            s["MIDDLEWARE_CLASSES"] = tuple(s["MIDDLEWARE_CLASSES"])
            s["MIDDLEWARE_CLASSES"] += (debug_mw,)
    if s.get("PACKAGE_NAME_FILEBROWSER") in s["INSTALLED_APPS"]:
        s["FILEBROWSER_URL_FILEBROWSER_MEDIA"] = "/filebrowser/media/"
        fb_path = path_for_import(s["PACKAGE_NAME_FILEBROWSER"])
        fb_media_path = os.path.join(fb_path, "media", "filebrowser")
        s["FILEBROWSER_PATH_FILEBROWSER_MEDIA"] = fb_media_path
    if s.get("PACKAGE_NAME_GRAPPELLI") in s["INSTALLED_APPS"]:
        s["GRAPPELLI_ADMIN_HEADLINE"] = "Mezzanine"
        s["GRAPPELLI_ADMIN_TITLE"] = "Mezzanine"
        grappelli_path = path_for_import(s["PACKAGE_NAME_GRAPPELLI"])
        s["GRAPPELLI_MEDIA_PATH"] = os.path.join(grappelli_path, "media")
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

    # Caching.
    if not s.get("CACHE_BACKEND"):
        s["CACHE_TIMEOUT"] = s["CACHE_MIDDLEWARE_SECONDS"] = 0
        try:
            import cmemcache
        except ImportError:
            try:
                import memcache
            except ImportError:
                s["CACHE_BACKEND"] = "locmem:///"
        if not s.get("CACHE_BACKEND"):
            s["CACHE_TIMEOUT"] = s["CACHE_MIDDLEWARE_SECONDS"] = 180
            s["CACHE_BACKEND"] = "memcached://127.0.0.1:11211/?timeout=%s" % \
                                                 s["CACHE_MIDDLEWARE_SECONDS"]
            s["CACHE_MIDDLEWARE_ANONYMOUS_ONLY"] = True
    if s.get("TESTING"):
        s["CACHE_BACKEND"] = "locmem:///"
        s["CACHE_MIDDLEWARE_SECONDS"] = 0

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
        s["TEMPLATE_DIRS"] = (theme_templates,) + tuple(s["TEMPLATE_DIRS"])
        
    # Remaining code is for Django 1.1 support.
    if VERSION >= (1, 2, 0):
        return
    # Add the dummy csrf_token template tag to builtins and remove 
    # Django's CsrfViewMiddleware.
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
