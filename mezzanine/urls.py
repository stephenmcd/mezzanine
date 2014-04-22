"""
This is the main ``urlconf`` for Mezzanine - it sets up patterns for
all the various Mezzanine apps, third-party apps like Grappelli and
filebrowser.
"""

from __future__ import unicode_literals
from future.builtins import str

from django.conf.urls import patterns, include
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
        exec("from %s import %s" % model)
    except ImportError:
        pass
    else:
        try:
            admin.site.unregister(eval(model[1]))
        except NotRegistered:
            pass


urlpatterns = []

# JavaScript localization feature
js_info_dict = {'domain': 'django'}
urlpatterns += patterns('django.views.i18n',
    (r'^jsi18n/(?P<packages>\S+?)/$', 'javascript_catalog', js_info_dict),
)

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
                                                content_type="text/plain")),
    )

# Miscellanous Mezzanine patterns.
urlpatterns += patterns("",
    ("^", include("mezzanine.core.urls")),
    ("^", include("mezzanine.generic.urls")),
)

# Mezzanine's Accounts app
_old_accounts_enabled = getattr(settings, "ACCOUNTS_ENABLED", False)
if _old_accounts_enabled:
    import warnings
    warnings.warn("The setting ACCOUNTS_ENABLED is deprecated. Please "
                  "add mezzanine.accounts to INSTALLED_APPS.")
if _old_accounts_enabled or "mezzanine.accounts" in settings.INSTALLED_APPS:
    # We don't define a URL prefix here such as /account/ since we want
    # to honour the LOGIN_* settings, which Django has prefixed with
    # /account/ by default. So those settings are used in accounts.urls
    urlpatterns += patterns("",
        ("^", include("mezzanine.accounts.urls")),
    )

# Mezzanine's Blog app.
blog_installed = "mezzanine.blog" in settings.INSTALLED_APPS
if blog_installed:
    BLOG_SLUG = settings.BLOG_SLUG.rstrip("/")
    blog_patterns = patterns("",
        ("^%s" % BLOG_SLUG, include("mezzanine.blog.urls")),
    )
    urlpatterns += blog_patterns

# Mezzanine's Pages app.
PAGES_SLUG = ""
if "mezzanine.pages" in settings.INSTALLED_APPS:
    # No BLOG_SLUG means catch-all patterns belong to the blog,
    # so give pages their own prefix and inject them before the
    # blog urlpatterns.
    if blog_installed and not BLOG_SLUG:
        PAGES_SLUG = getattr(settings, "PAGES_SLUG", "pages").strip("/") + "/"
        blog_patterns_start = urlpatterns.index(blog_patterns[0])
        urlpatterns[blog_patterns_start:len(blog_patterns)] = patterns("",
            ("^%s" % str(PAGES_SLUG), include("mezzanine.pages.urls")),
        )
    else:
        urlpatterns += patterns("",
            ("^", include("mezzanine.pages.urls")),
        )
