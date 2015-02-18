from __future__ import unicode_literals

import os
import sys
from warnings import warn

from django import VERSION
from django.conf import global_settings as defaults
from django.template.base import add_to_builtins

from mezzanine.utils.importing import path_for_import
from mezzanine.utils.timezone import get_best_local_timezone


class SitesAllowedHosts(object):
    """
    This is a fallback for Django 1.5's ALLOWED_HOSTS setting
    which is required when DEBUG is False. It looks up the
    ``Site`` model and uses any domains added to it, the
    first time the setting is accessed.
    """
    def __iter__(self):
        if getattr(self, "_hosts", None) is None:
            from django.contrib.sites.models import Site
            self._hosts = [s.domain.split(":")[0] for s in Site.objects.all()]
        return iter(self._hosts)


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

    if not s.get("ALLOWED_HOSTS", []):
        warn("You haven't defined the ALLOWED_HOSTS settings, which "
             "Django requires. Will fall back to the domains "
             "configured as sites.")
        s["ALLOWED_HOSTS"] = SitesAllowedHosts()

    if s.get("TIME_ZONE", None) is None:
        tz = get_best_local_timezone()
        s["TIME_ZONE"] = tz
        warn("TIME_ZONE setting is not set, using closest match: %s" % tz)

    # Define some settings based on management command being run.
    management_command = sys.argv[1] if len(sys.argv) > 1 else ""
    # Some kind of testing is running via test or testserver.
    s["TESTING"] = management_command in ("test", "testserver")
    # Some kind of development server is running via runserver,
    # runserver_plus or harvest (lettuce)
    s["DEV_SERVER"] = management_command.startswith(("runserver", "harvest"))

    # Change tuple settings to lists for easier manipulation.
    s.setdefault("AUTHENTICATION_BACKENDS", defaults.AUTHENTICATION_BACKENDS)
    s.setdefault("STATICFILES_FINDERS", defaults.STATICFILES_FINDERS)
    tuple_list_settings = ["AUTHENTICATION_BACKENDS", "INSTALLED_APPS",
                           "MIDDLEWARE_CLASSES", "STATICFILES_FINDERS",
                           "LANGUAGES", "TEMPLATE_CONTEXT_PROCESSORS"]
    for setting in tuple_list_settings[:]:
        if not isinstance(s.get(setting, []), list):
            s[setting] = list(s[setting])
        else:
            # Setting is already a list, so we'll exclude it from
            # the list of settings we'll revert back to tuples.
            tuple_list_settings.remove(setting)

    # From Mezzanine 3.1.2 and onward we added the context processor
    # for handling the page variable in templates - here we help
    # upgrading by adding it if missing, with a warning. This helper
    # can go away eventually.
    cp = "mezzanine.pages.context_processors.page"
    if ("mezzanine.pages" in s["INSTALLED_APPS"] and
            cp not in s["TEMPLATE_CONTEXT_PROCESSORS"]):
        warn("%s is required in the TEMPLATE_CONTEXT_PROCESSORS setting. "
             "Adding it now, but you should update settings.py to "
             "explicitly include it." % cp)
        append("TEMPLATE_CONTEXT_PROCESSORS", cp)

    # Set up cookie messaging if none defined.
    storage = "django.contrib.messages.storage.cookie.CookieStorage"
    s.setdefault("MESSAGE_STORAGE", storage)

    # If required, add django-modeltranslation for both tests and deployment
    if not s.get("USE_MODELTRANSLATION", False):
        remove("INSTALLED_APPS", "modeltranslation")
    else:
        try:
            __import__("modeltranslation")
        except ImportError:
            # django-modeltranslation is not installed, remove setting so
            # admin won't try to import it
            s["USE_MODELTRANSLATION"] = False
            remove("INSTALLED_APPS", "modeltranslation")
            warn("USE_MODETRANSLATION setting is set to True but django-"
                    "modeltranslation is not installed. Disabling it.")
        else:
            # Force i18n so we are assured that modeltranslation is active
            s["USE_I18N"] = True
            append("INSTALLED_APPS", "modeltranslation")

    # Setup for optional apps.
    optional = list(s.get("OPTIONAL_APPS", []))
    if s.get("USE_SOUTH") and VERSION < (1, 7):
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

    if s["TESTING"]:
        # Following bits are work-arounds for some assumptions that
        # Django 1.5's tests make.

        # Triggers interactive superuser creation and some pyc/pyo tests
        # fail with standard permissions.
        remove("INSTALLED_APPS", "django_extensions")

    # To support migrations for both Django 1.7 and South, South's old
    # migrations for each app were moved into "app.migrations.south"
    # packages. Here we assign each of these to SOUTH_MIGRATION_MODULES
    # allowing South to find them.
    if "south" in s["INSTALLED_APPS"]:
        s.setdefault("SOUTH_MIGRATION_MODULES", {})
        for app in s["INSTALLED_APPS"]:
            # We need to verify the path to the custom migrations
            # package exists for each app. We can't simply try
            # and import it, for some apps this causes side effects,
            # so we need to import something higher up to get at its
            # filesystem path - this can't be the actual app either,
            # side effects again, but we can generally import the
            # top-level package for apps that are contained within
            # one, which covers Mezzanine, Cartridge, Drum.
            if "." not in app:
                continue
            migrations = "%s.migrations.south" % app
            parts = migrations.split(".", 1)
            root = path_for_import(parts[0])
            other = parts[1].replace(".", os.sep)
            if os.path.exists(os.path.join(root, other)):
                s["SOUTH_MIGRATION_MODULES"][app.split(".")[-1]] = migrations

    if "debug_toolbar" in s["INSTALLED_APPS"]:
        debug_mw = "debug_toolbar.middleware.DebugToolbarMiddleware"
        append("MIDDLEWARE_CLASSES", debug_mw)
        # Ensure debug_toolbar is before modeltranslation to avoid
        # races for configuration.
        move("INSTALLED_APPS", "debug_toolbar", 0)

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
    else:
        s["GRAPPELLI_INSTALLED"] = True

    # Ensure admin is at the bottom of the app order so that admin
    # templates are loaded in the correct order, and that staticfiles
    # is also at the end so its runserver can be overridden.
    apps = ["django.contrib.admin"]
    if VERSION >= (1, 7):
        apps += ["django.contrib.staticfiles"]
    for app in apps:
        try:
            move("INSTALLED_APPS", app, len(s["INSTALLED_APPS"]))
        except ValueError:
            pass

    # Add missing apps if existing apps depend on them.
    if "mezzanine.blog" in s["INSTALLED_APPS"]:
        append("INSTALLED_APPS", "mezzanine.generic")
    if "mezzanine.generic" in s["INSTALLED_APPS"]:
        s.setdefault("COMMENTS_APP", "mezzanine.generic")
        append("INSTALLED_APPS", "django_comments")

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

    # If only LANGUAGE_CODE has been defined, ensure the other required
    # settings for translations are configured.
    if (s.get("LANGUAGE_CODE") and len(s.get("LANGUAGES", [])) == 1 and
            s["LANGUAGE_CODE"] != s["LANGUAGES"][0][0]):
        s["USE_I18N"] = True
        s["LANGUAGES"] = [(s["LANGUAGE_CODE"], "")]

    # Revert tuple settings back to tuples.
    for setting in tuple_list_settings:
        s[setting] = tuple(s[setting])

    # Some settings tweaks for different DB engines.
    for (key, db) in s["DATABASES"].items():
        shortname = db["ENGINE"].split(".")[-1]
        if shortname == "sqlite3":
            # If the Sqlite DB name doesn't contain a path, assume
            # it's in the project directory and add the path to it.
            if "NAME" in db and os.sep not in db["NAME"]:
                db_path = os.path.join(s.get("PROJECT_ROOT", ""), db["NAME"])
                s["DATABASES"][key]["NAME"] = db_path
        elif shortname == "mysql":
            # Required MySQL collation for tests.
            s["DATABASES"][key]["TEST_COLLATION"] = "utf8_general_ci"
