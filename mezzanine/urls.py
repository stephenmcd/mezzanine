"""
This is the main ``urlconf`` for Mezzanine - it sets up patterns for
all the various Mezzanine apps, third-party apps like Grappelli and
filebrowser.
"""

from urlparse import urlsplit

from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.http import HttpResponse

from mezzanine.conf import settings
from mezzanine.core.sitemaps import DisplayableSitemap


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

# Django's sitemap app.
if "django.contrib.sitemaps" in settings.INSTALLED_APPS:
    sitemaps = {"sitemaps": {"all": DisplayableSitemap}}
    urlpatterns += patterns("django.contrib.sitemaps.views",
        ("^sitemap\.xml$", "sitemap", sitemaps)
    )

# Return a robots.txt that disallows all spiders when DEBUG is True.
if getattr(settings, "DEBUG", False):
    urlpatterns += patterns("",
        ("^robots.txt$", lambda r: HttpResponse("User-agent: *\nDisallow: /",
                                                mimetype="text/plain")),
    )

# Filebrowser admin media library.
if getattr(settings, "PACKAGE_NAME_FILEBROWSER") in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^admin/media-library/", include("%s.urls" %
                                        settings.PACKAGE_NAME_FILEBROWSER)),
    )

# Grappelli admin skin.
_pattern = urlsplit(settings.ADMIN_MEDIA_PREFIX).path.strip("/").split("/")[0]
if getattr(settings, "PACKAGE_NAME_GRAPPELLI") in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^grappelli/", include("%s.urls" % settings.PACKAGE_NAME_GRAPPELLI)),
    )

# Miscellanous Mezzanine patterns.
urlpatterns += patterns("",
    ("^", include("mezzanine.core.urls")),
    ("^", include("mezzanine.generic.urls")),
)

# Mezzanine's Blog app.
BLOG_SLUG = settings.BLOG_SLUG
blog_installed = "mezzanine.blog" in settings.INSTALLED_APPS
if blog_installed:
    if BLOG_SLUG:
        BLOG_SLUG += "/"
    urlpatterns += patterns("",
        ("^%s" % BLOG_SLUG, include("mezzanine.blog.urls")),
    )

# Mezzanine's Pages app.
PAGES_SLUG = ""
if "mezzanine.pages" in settings.INSTALLED_APPS:
    # No BLOG_SLUG means catch-all patterns belong to the blog,
    # so give pages their own prefix.
    if not BLOG_SLUG and blog_installed:
        PAGES_SLUG = "pages/"
        urlpatterns[-1:1] = patterns("",
            ("^%s" % PAGES_SLUG, include("mezzanine.pages.urls")),
        )
    else:
        urlpatterns += patterns("",
            ("^", include("mezzanine.pages.urls")),
        )
