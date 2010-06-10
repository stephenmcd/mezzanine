
# Main Django settings.
DEBUG = False
DEV_SERVER = False
MANAGERS = ADMINS = ()
TIME_ZONE = "Australia/Melbourne"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
LANGUAGE_CODE = "en"
SITE_ID = 1
USE_I18N = False
SECRET_KEY = "5tve)^cpj9gsdfg54445364TW#$%u=!p2aqwtjiwxzzt%g6p"
INTERNAL_IPS = ("127.0.0.1",)
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.load_template_source",
    "django.template.loaders.app_directories.load_template_source",
)

# Database.
DATABASE_ENGINE = ""
DATABASE_NAME = ""
DATABASE_USER = ""
DATABASE_PASSWORD = ""
DATABASE_HOST = ""
DATABASE_PORT = ""

# Paths.
import os
project_path = os.path.dirname(os.path.abspath(__file__))
project_dir = project_path.split(os.sep)[-1]
MEDIA_URL = "/site_media/"
MEDIA_ROOT = os.path.join(project_path, MEDIA_URL.strip("/"))
TEMPLATE_DIRS = (os.path.join(project_path, "templates"),)
ADMIN_MEDIA_PREFIX = "/media/"
ROOT_URLCONF = "%s.urls" % project_dir
CACHE_MIDDLEWARE_KEY_PREFIX = project_dir
if DATABASE_ENGINE == "sqlite3":
    DATABASE_NAME = os.path.join(project_path, DATABASE_NAME)

# Apps.
INSTALLED_APPS = (
    "mezzanine.core",
    "mezzanine.blog",
    "mezzanine.pages",
    "mezzanine.twitter",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "mezzanine.core.middleware.MobileTemplate",
)

# Optional apps.
import sys
OPTIONAL_APPS = (
    {"apps": ("debug_toolbar",), 
        "middleware": ("debug_toolbar.middleware.DebugToolbarMiddleware",)},
    {"apps": ("south",), 
        "condition": not (len(sys.argv) > 1 and sys.argv[1] == "test")},
    {"apps": ("django_extensions",)},
    {"apps": ("filebrowser",)},
    {"apps": ("grappelli_safe",)},
    {"apps": ("gunicorn",)},
)
for app in OPTIONAL_APPS:
    if app.get("condition", True):
        try:
            __import__(app.get("import", app["apps"][0]))
        except ImportError:
            pass
        else:
            INSTALLED_APPS += app.get("apps", ())
            MIDDLEWARE_CLASSES += app.get("middleware", ())
            TEMPLATE_CONTEXT_PROCESSORS += app.get("context_processors", ())
INSTALLED_APPS = sorted(INSTALLED_APPS, key=lambda s: s.startswith("django."))

# Optional apps settings.
if "debug_toolbar" in INSTALLED_APPS:
    DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
if "grappelli_safe" in INSTALLED_APPS:
    GRAPPELLI_ADMIN_HEADLINE = "Mezzanine"
    GRAPPELLI_ADMIN_TITLE = "Mezzanine"
    GRAPPELLI_MEDIA_PATH = os.path.join(os.path.dirname(
        __import__("grappelli_safe").__file__), "media")
if "filebrowser" in INSTALLED_APPS:
    FILEBROWSER_URL_FILEBROWSER_MEDIA = "/filebrowser/media/"
    FILEBROWSER_PATH_FILEBROWSER_MEDIA = os.path.join(os.path.dirname(
        __import__("filebrowser").__file__), "media", "filebrowser")

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
    CACHE_BACKEND = "memcached://127.0.0.1:11211/?timeout=%s" % CACHE_MIDDLEWARE_SECONDS
    CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Local settings.
try:
    from local_settings import *
except ImportError:
    pass

TEMPLATE_DEBUG = DEBUG
if DEV_SERVER and "grappelli_safe" in INSTALLED_APPS:
    ADMIN_MEDIA_PREFIX = "http://127.0.0.1:8000/media/admin/"

