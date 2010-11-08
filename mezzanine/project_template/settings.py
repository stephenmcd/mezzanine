
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
    "django.core.context_processors.auth",
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
    "django.middleware.cache.FetchFromCacheMiddleware",
    "mezzanine.core.middleware.MobileTemplate",
    "mezzanine.core.middleware.AdminLoginInterfaceSelector",
)

# For > Django 1.2 add the CSRF middleware. For earlier, add the dummy
# csrf_token template tag to builtins.
from django import VERSION
if VERSION[0] <= 1 and VERSION[1] <= 1:
    from django.template.loader import add_to_builtins
    add_to_builtins("mezzanine.core.templatetags.dummy_csrf")
else:
    MIDDLEWARE_CLASSES += ("django.middleware.csrf.CsrfViewMiddleware",)

# Store these package names here as they may change in the future since at the
# moment we are using custom forks of them.
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
if "debug_toolbar" in INSTALLED_APPS:
    DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
    MIDDLEWARE_CLASSES += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
if PACKAGE_NAME_GRAPPELLI in INSTALLED_APPS:
    ADMIN_MEDIA_PREFIX = "/media/admin/"
    GRAPPELLI_ADMIN_HEADLINE = "Mezzanine"
    GRAPPELLI_ADMIN_TITLE = "Mezzanine"
    GRAPPELLI_MEDIA_PATH = os.path.join(os.path.dirname(
        __import__(PACKAGE_NAME_GRAPPELLI).__file__), "media")
if PACKAGE_NAME_FILEBROWSER in INSTALLED_APPS:
    FILEBROWSER_URL_FILEBROWSER_MEDIA = "/filebrowser/media/"
    FILEBROWSER_PATH_FILEBROWSER_MEDIA = os.path.join(os.path.dirname(
        __import__(PACKAGE_NAME_FILEBROWSER).__file__), "media", "filebrowser")

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

TEMPLATE_DEBUG = DEBUG

command = ""
if len(sys.argv) >= 2:
    command = sys.argv[1]

if command == "runserver" and PACKAGE_NAME_GRAPPELLI in INSTALLED_APPS:
    # Adopted from django.core.management.commands.runserver - easiest way 
    # so far to actually get all the media for grappelli working with the dev 
    # server is to hard-code the host:port to ``ADMIN_MEDIA_PREFIX``, so 
    # here we check for a custom host:port before doing this.
    addrport = ""
    if len(sys.argv) > 2:
        addrport = sys.argv[2]
    if not addrport:
        addr = ""
        port = "8000"
    else:
        try:
            addr, port = addrport.split(":")
        except ValueError:
            addr, port = "", addrport
    if not addr:
        addr = "127.0.0.1"
    ADMIN_MEDIA_PREFIX = "http://%s:%s%s" % (addr, port, ADMIN_MEDIA_PREFIX)

multi_db = (not globals().get("DATABASE_ENGINE")) and "DATABASES" in globals()
if multi_db:
    dbs = DATABASES
else:
    dbs = {None: {"ENGINE": DATABASE_ENGINE, "NAME": DATABASE_NAME}}
for key, db in dbs.items():
    engine = db["ENGINE"].split(".")[-1]
    if engine == "sqlite3" and os.sep not in db["NAME"]:
        # If the sqlite DB name doesn't contain a path, assume it's in the 
        # project directory and add the path to it.
        name = os.path.join(project_path, db["NAME"])
        if multi_db:
            DATABASES[key]["NAME"] = name
        else:
            DATABASE_NAME = name
    elif engine == "mysql":
        # Required MySQL collation for tests.
        collation = "utf8_general_ci"
        if multi_db:
            DATABASES[key]["TEST_COLLATION"] = collation
        else:
            TEST_DATABASE_COLLATION = collation
    elif engine.startswith("postgresql") and not globals().get("TIME_ZONE", 1):
        # Specifying a blank time zone to fall back to the system's time zone
        # will break table creation in Postgres so remove it.
        del TIME_ZONE
