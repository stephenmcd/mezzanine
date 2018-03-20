from __future__ import unicode_literals

import os
import sys
from inspect import getmro
from warnings import warn

import six
from django.db import OperationalError
from django.conf import global_settings as defaults
from django.utils.module_loading import import_string

from mezzanine.utils.deprecation import get_middleware_setting
from mezzanine.utils.timezone import get_best_local_timezone


class SitesAllowedHosts(object):
    """
    This is a fallback for Django's ALLOWED_HOSTS setting
    which is required when DEBUG is False. It looks up the
    ``Site`` model and uses any domains added to it, the
    first time the setting is accessed.
    """
    def __iter__(self):
        if getattr(self, "_hosts", None) is None:
            from django.contrib.sites.models import Site
            try:
                self._hosts = [
                    s.domain.split(":")[0] for s in Site.objects.all()
                ]
            except OperationalError:
                return iter([])
        return iter(self._hosts)

    def __add__(self, other):
        return list(self) + other


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

    # Django 1.10 middleware compatibility
    MIDDLEWARE_SETTING_NAME = 'MIDDLEWARE' if 'MIDDLEWARE' in s \
                            and s['MIDDLEWARE'] is not None \
                            else 'MIDDLEWARE_CLASSES'

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
                           MIDDLEWARE_SETTING_NAME, "STATICFILES_FINDERS",
                           "LANGUAGES", "TEMPLATE_CONTEXT_PROCESSORS"]
    for setting in tuple_list_settings[:]:
        if not isinstance(s.get(setting, []), list):
            s[setting] = list(s[setting])
        else:
            # Setting is already a list, so we'll exclude it from
            # the list of settings we'll revert back to tuples.
            tuple_list_settings.remove(setting)

    # Set up cookie messaging if none defined.
    storage = "django.contrib.messages.storage.cookie.CookieStorage"
    s.setdefault("MESSAGE_STORAGE", storage)

    # If required, add django-modeltranslation for both tests and deployment
    if not s.get("USE_MODELTRANSLATION", False) or s["TESTING"]:
        s["USE_MODELTRANSLATION"] = False
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
    for app in optional:
        if app not in s["INSTALLED_APPS"]:
            try:
                __import__(app)
            except ImportError:
                pass
            else:
                s["INSTALLED_APPS"].append(app)

    if s["TESTING"]:
        # Triggers interactive superuser creation and some pyc/pyo tests
        # fail with standard permissions.
        remove("INSTALLED_APPS", "django_extensions")

    if "debug_toolbar" in s["INSTALLED_APPS"]:
        # We need to configure debug_toolbar manually otherwise it
        # breaks in conjunction with modeltranslation. See the
        # "Explicit setup" section in debug_toolbar docs for more info.
        s["DEBUG_TOOLBAR_PATCH_SETTINGS"] = False
        debug_mw = "debug_toolbar.middleware.DebugToolbarMiddleware"
        append(MIDDLEWARE_SETTING_NAME, debug_mw)
        s.setdefault("INTERNAL_IPS", ("127.0.0.1",))

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
    for app in ["django.contrib.admin", "django.contrib.staticfiles"]:
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
        s[MIDDLEWARE_SETTING_NAME] = [mw for mw in s[MIDDLEWARE_SETTING_NAME]
                                   if not
                                   (mw.endswith("UpdateCacheMiddleware") or
                                    mw.endswith("FetchFromCacheMiddleware"))]

    # If only LANGUAGE_CODE has been defined, ensure the other required
    # settings for translations are configured.
    if (s.get("LANGUAGE_CODE") and len(s.get("LANGUAGES", [])) == 1 and
            s["LANGUAGE_CODE"] != s["LANGUAGES"][0][0]):
        s["USE_I18N"] = True
        s["LANGUAGES"] = [(s["LANGUAGE_CODE"], "")]

    # Ensure required middleware is installed, otherwise admin
    # becomes inaccessible.
    if s["USE_I18N"] and not [mw for mw in s[MIDDLEWARE_SETTING_NAME] if
            mw.endswith("LocaleMiddleware")]:
        session = s[MIDDLEWARE_SETTING_NAME].index(
            "django.contrib.sessions.middleware.SessionMiddleware")
        s[MIDDLEWARE_SETTING_NAME].insert(session + 1,
            "django.middleware.locale.LocaleMiddleware")

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
                db["NAME"] = db_path
        elif shortname == "mysql":
            # Required MySQL collation for tests.
            db.setdefault("TEST", {})["COLLATION"] = "utf8_general_ci"


def real_project_name(project_name):
    """
    Used to let Mezzanine run from its project template directory, in which
    case "{{ project_name }}" won't have been replaced by a real project name.
    """
    if project_name == "{{ project_name }}":
        return "project_name"
    return project_name


def middlewares_or_subclasses_installed(needed_middlewares):
    """
    When passed an iterable of dotted strings, returns True if all
    of the middlewares (or their subclasses) are installed.
    """
    middleware_setting = set(get_middleware_setting())

    # Shortcut case, check by string
    if all(m in middleware_setting for m in needed_middlewares):
        return True

    def flatten(seqs):
        return (item for seq in seqs for item in seq)

    middleware_items = map(import_string, middleware_setting)
    middleware_classes = filter(
        lambda m: isinstance(m, six.class_types),
        middleware_items)
    middleware_ancestors = set(flatten(map(getmro, middleware_classes)))

    needed_middlewares = set(map(import_string, needed_middlewares))

    return needed_middlewares.issubset(middleware_ancestors)
