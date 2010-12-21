
# Mezzanine settings.
THEME = ""

# Main Django settings.
TIME_ZONE = ""
DEBUG = False
DEV_SERVER = False
MANAGERS = ADMINS = ()
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
LANGUAGE_CODE = "en"
SITE_ID = 1
USE_I18N = False
SECRET_KEY = "%(SECRET_KEY)s"
INTERNAL_IPS = ("127.0.0.1",)
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

# Databases.
DATABASES = {
    "default": {
        # "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "ENGINE": "",
        # DB name or path to database file if using sqlite3.
        "NAME": "",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
         # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}

# Paths.
import os
_project_path = os.path.dirname(os.path.abspath(__file__))
_project_dir = _project_path.split(os.sep)[-1]
ADMIN_MEDIA_PREFIX = "/media/"
CACHE_MIDDLEWARE_KEY_PREFIX = _project_dir
MEDIA_URL = "/site_media/"
MEDIA_ROOT = os.path.join(_project_path, MEDIA_URL.strip("/"))
ROOT_URLCONF = "%s.urls" % _project_dir
TEMPLATE_DIRS = (os.path.join(_project_path, "templates"),)

# Apps.
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.blog",
    "mezzanine.forms",
    "mezzanine.pages",
    "mezzanine.twitter",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "mezzanine.conf.context_processors.settings",
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "mezzanine.core.middleware.DeviceAwareUpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "mezzanine.core.middleware.DeviceAwareFetchFromCacheMiddleware",
    "mezzanine.core.middleware.AdminLoginInterfaceSelector",
)

# Store these package names here as they may change in the future since
# at the moment we are using custom forks of them.
PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"

# Optional apps - these will be added to ``INSTALLED_APPS`` if available.
OPTIONAL_APPS = (
    "debug_toolbar",
    "south",
    "django_extensions",
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}

import sys
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"
if not TESTING:
    for app in OPTIONAL_APPS:
        try:
            __import__(app)
        except ImportError:
            pass
        else:
            INSTALLED_APPS += (app,)
INSTALLED_APPS = sorted(list(INSTALLED_APPS), reverse=True)

# Local settings.
try:
    from local_settings import *
except ImportError:
    pass

# Dynamic settings.
from mezzanine.utils.conf import set_dynamic_settings
set_dynamic_settings(globals())
