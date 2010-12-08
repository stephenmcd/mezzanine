"""
This is the main ``urlconf`` for Mezzanine - it sets up patterns for 
all the various Mezzanine apps, third-party apps like Grappelli and 
filebrowser, and adds some handling for media files during development 
when the ``runserver`` command is being used, that also deals with 
hosting theme development when the ``THEME`` setting is defined.
"""

from urlparse import urlsplit

from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
 
from mezzanine.conf import settings
from mezzanine.utils.urls import static_urls


# Remove unwanted models from the admin that are installed by default with
# third-party apps.
for model in settings.ADMIN_REMOVAL:
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


urlpatterns = []

# Filebrowser admin media library.
if getattr(settings, "PACKAGE_NAME_FILEBROWSER") in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^admin/filebrowser/", include("%s.urls" % 
                                        settings.PACKAGE_NAME_FILEBROWSER)),
        static_urls(settings.FILEBROWSER_URL_FILEBROWSER_MEDIA.strip("/"), 
                    settings.FILEBROWSER_PATH_FILEBROWSER_MEDIA),
    )

# Grappelli admin skin.
_pattern = urlsplit(settings.ADMIN_MEDIA_PREFIX).path.strip("/").split("/")[0]
if getattr(settings, "PACKAGE_NAME_GRAPPELLI") in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^grappelli/", include("%s.urls" % settings.PACKAGE_NAME_GRAPPELLI)),
        static_urls(_pattern, settings.GRAPPELLI_MEDIA_PATH),
    )

# Miscellanous Mezzanine patterns.
urlpatterns += patterns("",
    ("^mezzanine/", include("mezzanine.core.urls")),
    static_urls(settings.CONTENT_MEDIA_URL, settings.CONTENT_MEDIA_PATH),
)

# Mezzanine's Blog app.
if "mezzanine.blog" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^%s/" % settings.BLOG_SLUG, include("mezzanine.blog.urls")),
    )

# Mezzanine's Pages app.
if "mezzanine.pages" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^", include("mezzanine.pages.urls")),
    )

# Hosting of static assets when using built-in runserver during development.
if getattr(settings, "DEV_SERVER", False):
    _pattern = "^%s/(?P<path>.*)$" % settings.MEDIA_URL.strip("/")
    urlpatterns += patterns("",
        (_pattern, "mezzanine.core.views.serve_with_theme"),
    )
