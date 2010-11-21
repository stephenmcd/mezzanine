
# Mezzanine settings.
THEME = ""

# Main Django settings.
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
        "ENGINE": "",
        "HOST": "",
        "NAME": "",
        "PASSWORD": "",
        "PORT": "",
        "USER": "",
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
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "mezzanine.core.middleware.MobileTemplate",
    "mezzanine.core.middleware.AdminLoginInterfaceSelector",
)

# Store these package names here as they may change in the future since 
# at the moment we are using custom forks of them.
PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"

# Optional apps.
OPTIONAL_APPS = (
    "debug_toolbar",
    "south",
    "django_extensions",
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

import sys
if not (len(sys.argv) > 1 and sys.argv[1] == "test"):
    for app in OPTIONAL_APPS:
        try:
            __import__(app)
        except ImportError:
            pass
        else:
            INSTALLED_APPS += (app,)
INSTALLED_APPS = sorted(list(INSTALLED_APPS), reverse=True)

# Optional app settings.
from mezzanine.utils import path_for_import, set_dynamic_settings
if "debug_toolbar" in INSTALLED_APPS:
    DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
    MIDDLEWARE_CLASSES += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
if PACKAGE_NAME_GRAPPELLI in INSTALLED_APPS:
    GRAPPELLI_ADMIN_HEADLINE = "Mezzanine"
    GRAPPELLI_ADMIN_TITLE = "Mezzanine"
    GRAPPELLI_MEDIA_PATH = os.path.join(
                             path_for_import(PACKAGE_NAME_GRAPPELLI), "media")
if PACKAGE_NAME_FILEBROWSER in INSTALLED_APPS:
    FILEBROWSER_URL_FILEBROWSER_MEDIA = "/filebrowser/media/"
    FILEBROWSER_PATH_FILEBROWSER_MEDIA = os.path.join(
            path_for_import(PACKAGE_NAME_FILEBROWSER), "media", "filebrowser")

# Caching.
CACHE_BACKEND = ""
CACHE_TIMEOUT = CACHE_MIDDLEWARE_SECONDS = 0
try:
    import cmemcache
except ImportError:
    try:
        import memcache
    except ImportError:
        CACHE_BACKEND = "locmem:///"
if not CACHE_BACKEND:
    CACHE_TIMEOUT = CACHE_MIDDLEWARE_SECONDS = 180
    CACHE_BACKEND = "memcached://127.0.0.1:11211/?timeout=%s" % \
                                                    CACHE_MIDDLEWARE_SECONDS
    CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Local settings.
try:
    from local_settings import *
except ImportError:
    pass
    
# Dynamic settings.
set_dynamic_settings(globals())
