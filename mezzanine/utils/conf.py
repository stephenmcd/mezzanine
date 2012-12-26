
import os
import sys

from django.conf.global_settings import STATICFILES_FINDERS
from django.template.loader import add_to_builtins


def set_dynamic_settings(s):
    """
    Called at the end of the project's settings module, and is passed
    its globals dict for updating with some final tweaks for settings
    that generally aren't specified, but can be given some better
    defaults based on other settings that have been specified. Broken
    out into its own function so that the code need not be replicated
    in the settings modules of other project-based apps that leverage
    Mezzanine's settings module.
    """

    # Moves an existing list setting value to a different position.
    move = lambda n, k, i: s[n].insert(i, s[n].pop(s[n].index(k)))
    # Add a value to the end of a list setting if not in the list.
    append = lambda n, k: s[n].append(k) if k not in s[n] else None
    # Add a value to the start of a list setting if not in the list.
    prepend = lambda n, k: s[n].insert(0, k) if k not in s[n] else None
    # Remove a value from a list setting if in the list.
    remove = lambda n, k: s[n].remove(k) if k in s[n] else None

    s["TEMPLATE_DEBUG"] = s.get("TEMPLATE_DEBUG", s.get("DEBUG", False))
    add_to_builtins("mezzanine.template.loader_tags")
    # Define some settings based on management command being run.
    management_command = sys.argv[1] if len(sys.argv) > 1 else ""
    # Some kind of testing is running via test or testserver.
    s["TESTING"] = management_command.startswith("test")
    # Some kind of development server is running via runserver,
    # runserver_plus or harvest (lettuce)
    s["DEV_SERVER"] = management_command.startswith(("runserver", "harvest"))
    # Change tuple settings to lists for easier manipulation.
    s["INSTALLED_APPS"] = list(s["INSTALLED_APPS"])
    s["MIDDLEWARE_CLASSES"] = list(s["MIDDLEWARE_CLASSES"])
    s["STATICFILES_FINDERS"] = list(s.get("STATICFILES_FINDERS",
                                    STATICFILES_FINDERS))

    if s["DEV_SERVER"]:
        s["STATICFILES_DIRS"] = list(s.get("STATICFILES_DIRS", []))
        s["STATICFILES_DIRS"].append(s.pop("STATIC_ROOT"))

    # Set up cookie messaging if none defined.
    storage = "django.contrib.messages.storage.cookie.CookieStorage"
    s.setdefault("MESSAGE_STORAGE", storage)

    if s["TESTING"]:
        # Enable accounts when testing so the URLs exist.
        append("INSTALLED_APPS", "mezzanine.accounts")
        # New Django 1.5 tests in redirects app don't work with a
        # catch-all urlpattern such as Mezzanine's pages app.
        remove("INSTALLED_APPS", "django.contrib.redirects")
        remove("MIDDLEWARE_CLASSES",
            "django.contrib.redirects.middleware.RedirectFallbackMiddleware")
    else:
        # Setup for optional apps.
        optional = list(s.get("OPTIONAL_APPS", []))
        if s.get("USE_SOUTH"):
            optional.append("south")
        elif not s.get("USE_SOUTH", True) and "south" in s["INSTALLED_APPS"]:
            s["INSTALLED_APPS"].remove("south")
        for app in optional:
            if app not in s["INSTALLED_APPS"]:
                try:
                    __import__(app)
                except ImportError:
                    pass
                else:
                    s["INSTALLED_APPS"].append(app)
    if "debug_toolbar" in s["INSTALLED_APPS"]:
        debug_mw = "debug_toolbar.middleware.DebugToolbarMiddleware"
        prepend("MIDDLEWARE_CLASSES", debug_mw)
    # If compressor installed, ensure it's configured and make
    # Mezzanine's settings available to its offline context,
    # since jQuery is configured via a setting.
    if "compressor" in s["INSTALLED_APPS"]:
        append("STATICFILES_FINDERS", "compressor.finders.CompressorFinder")
        s.setdefault("COMPRESS_OFFLINE_CONTEXT", {
            "MEDIA_URL": s.get("MEDIA_URL", ""),
            "STATIC_URL": s.get("STATIC_URL", ""),
        })

        def mezzanine_settings():
            from mezzanine.conf import settings
            return settings
        s["COMPRESS_OFFLINE_CONTEXT"]["settings"] = mezzanine_settings

    # Ensure the Mezzanine auth backend is enabled if
    # mezzanine.accounts is being used.
    if "mezzanine.accounts" in s["INSTALLED_APPS"]:
        auth_backend = "mezzanine.core.auth_backends.MezzanineBackend"
        s.setdefault("AUTHENTICATION_BACKENDS", [])
        prepend("AUTHENTICATION_BACKENDS", auth_backend)

    # Ensure Grappelli is after Mezzanine in app order so that
    # admin templates are loaded in the correct order.
    grappelli_name = s.get("PACKAGE_NAME_GRAPPELLI")
    try:
        move("INSTALLED_APPS", grappelli_name, len(s["INSTALLED_APPS"]))
    except ValueError:
        s["GRAPPELLI_INSTALLED"] = False
        s["ADMIN_MEDIA_PREFIX"] = s["STATIC_URL"] + "admin/"
    else:
        s["GRAPPELLI_INSTALLED"] = True
        s.setdefault("GRAPPELLI_ADMIN_HEADLINE", "Mezzanine")
        s.setdefault("GRAPPELLI_ADMIN_TITLE", "Mezzanine")

    # Ensure admin is last in the app order so that admin templates
    # are loaded in the correct order.
    move("INSTALLED_APPS", "django.contrib.admin", len(s["INSTALLED_APPS"]))

    # Add missing apps if existing apps depend on them.
    if "mezzanine.blog" in s["INSTALLED_APPS"]:
        append("INSTALLED_APPS", "mezzanine.generic")
    if "mezzanine.generic" in s["INSTALLED_APPS"]:
        s.setdefault("COMMENTS_APP", "mezzanine.generic")
        append("INSTALLED_APPS", "django.contrib.comments")

    # Ensure mezzanine.boot is first.
    try:
        move("INSTALLED_APPS", "mezzanine.boot", 0)
    except ValueError:
        pass

    # Remove caching middleware if no backend defined.
    if not (s.get("CACHE_BACKEND") or s.get("CACHES")):
        s["MIDDLEWARE_CLASSES"] = [mw for mw in s["MIDDLEWARE_CLASSES"] if not
                                   (mw.endswith("UpdateCacheMiddleware") or
                                    mw.endswith("FetchFromCacheMiddleware"))]

    # Some settings tweaks for different DB engines.
    for (key, db) in s["DATABASES"].items():
        shortname = db["ENGINE"].split(".")[-1]
        if shortname == "sqlite3" and os.sep not in db["NAME"]:
            # If the Sqlite DB name doesn't contain a path, assume
            # it's in the project directory and add the path to it.
            db_path = os.path.join(s.get("PROJECT_ROOT", ""), db["NAME"])
            s["DATABASES"][key]["NAME"] = db_path
        elif shortname == "mysql":
            # Required MySQL collation for tests.
            s["DATABASES"][key]["TEST_COLLATION"] = "utf8_general_ci"

    # Remaining is for Django < 1.4
    from django import VERSION
    if VERSION >= (1, 4):
        return
    s["TEMPLATE_CONTEXT_PROCESSORS"] = list(s["TEMPLATE_CONTEXT_PROCESSORS"])
    remove("TEMPLATE_CONTEXT_PROCESSORS", "django.core.context_processors.tz")
