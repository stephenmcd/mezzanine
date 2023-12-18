"""
This is the main ``urlconf`` for Mezzanine - it sets up patterns for
all the various Mezzanine apps, third-party apps like Grappelli and
filebrowser.
"""
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog

from mezzanine.conf import settings
from mezzanine.core.sitemaps import DisplayableSitemap

urlpatterns = []

# JavaScript localization feature
js_info_dict = {"domain": "django"}
urlpatterns += [
    re_path(r"^jsi18n/(?P<packages>\S+?)/$", JavaScriptCatalog.as_view(), js_info_dict),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]

# Django's sitemap app.
if "django.contrib.sitemaps" in settings.INSTALLED_APPS:
    sitemaps = {"sitemaps": {"all": DisplayableSitemap}}
    urlpatterns += [
        path("sitemap.xml", sitemap, sitemaps),
    ]

# Return a robots.txt that disallows all spiders when DEBUG is True.
if getattr(settings, "DEBUG", False):
    urlpatterns += [
        path(
            "robots.txt",
            lambda r: HttpResponse(
                "User-agent: *\nDisallow: /", content_type="text/plain"
            ),
        ),
    ]

# Miscellanous Mezzanine patterns.
urlpatterns += [
    path("", include("mezzanine.core.urls")),
    path("", include("mezzanine.generic.urls")),
]

# Mezzanine's Accounts app
if "mezzanine.accounts" in settings.INSTALLED_APPS:
    # We don't define a URL prefix here such as /account/ since we want
    # to honour the LOGIN_* settings, which Django has prefixed with
    # /account/ by default. So those settings are used in accounts.urls
    urlpatterns += [
        path("", include("mezzanine.accounts.urls")),
    ]

# Mezzanine's Blog app.
blog_installed = "mezzanine.blog" in settings.INSTALLED_APPS
if blog_installed:
    BLOG_SLUG = settings.BLOG_SLUG.rstrip("/")
    if BLOG_SLUG:
        BLOG_SLUG += "/"
    blog_patterns = [
        path(BLOG_SLUG, include("mezzanine.blog.urls")),
    ]
    urlpatterns += blog_patterns

# Mezzanine's Pages app.
PAGES_SLUG = ""
if "mezzanine.pages" in settings.INSTALLED_APPS:
    # No BLOG_SLUG means catch-all patterns belong to the blog,
    # so give pages their own prefix and inject them before the
    # blog urlpatterns.
    if blog_installed and not BLOG_SLUG.rstrip("/"):
        PAGES_SLUG = str(getattr(settings, "PAGES_SLUG", "pages").strip("/") + "/")
        blog_patterns_start = urlpatterns.index(blog_patterns[0])
        urlpatterns[blog_patterns_start : len(blog_patterns)] = [
            path(PAGES_SLUG, include("mezzanine.pages.urls")),
        ]
    else:
        urlpatterns += [
            path("", include("mezzanine.pages.urls")),
        ]
