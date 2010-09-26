
from urlparse import urlsplit

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.views.generic.simple import direct_to_template

from mezzanine.settings import ADMIN_REMOVAL, CONTENT_MEDIA_PATH, \
    CONTENT_MEDIA_URL

urlpatterns = patterns("mezzanine.core.views",
    url("^admin_keywords_submit/$", "admin_keywords_submit",
        name="admin_keywords_submit"),
    url("^edit/$", "edit", name="edit"),
    url("^search/$", "search", name="search"),
)

urlpatterns += patterns("",
    ("^%s/(?P<path>.*)$" % CONTENT_MEDIA_URL.strip("/"),
        "django.views.static.serve", {'document_root': CONTENT_MEDIA_PATH}),
)

# Remove unwanted models from the admin that are installed by default with
# third-party apps.
for model in ADMIN_REMOVAL:
    try:
        model = tuple(model.rsplit(".", 1))
        exec "from %s import %s" % model
    except ImportError:
        pass
    else:
        try:
            admin.site.unregister(eval(model[1]))
        except NotRegistered:
            pass

# Pairs of optional app names and their urlpatterns.
OPTIONAL_APP_PATTERNS = (
    (settings.PACKAGE_NAME_FILEBROWSER, patterns("",
        ("^admin/filebrowser/", include("%s.urls" %
            settings.PACKAGE_NAME_FILEBROWSER)),
        ("^%s/(?P<path>.*)$" % getattr(settings,
            "FILEBROWSER_URL_FILEBROWSER_MEDIA", "").strip("/"),
            "django.views.static.serve", {'document_root':
            getattr(settings, "FILEBROWSER_PATH_FILEBROWSER_MEDIA", "")}),
    )),
    (settings.PACKAGE_NAME_GRAPPELLI, patterns("",
        ("^grappelli/", include("%s.urls" %
            settings.PACKAGE_NAME_GRAPPELLI)),
        ("^%s/admin/(?P<path>.*)$" % urlsplit(settings.ADMIN_MEDIA_PREFIX
            ).path.strip("/").split("/")[0], "django.views.static.serve",
            {'document_root': getattr(settings, "GRAPPELLI_MEDIA_PATH", "")}),
    )),
)

# Add patterns for optionally installed apps.
for (app, app_patterns) in OPTIONAL_APP_PATTERNS:
    if app in settings.INSTALLED_APPS:
        urlpatterns += app_patterns

# Homepage.
urlpatterns += patterns("",
    url("^$", direct_to_template, {"template": "index.html"}, name="home"),
)
