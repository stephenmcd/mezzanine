
import os

from django.conf.urls.defaults import *

from mezzanine.conf import settings
from mezzanine.utils.path import path_for_import


urlpatterns = patterns("",
    ("^", include("mezzanine.core.urls")),
)

if "mezzanine.blog" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^%s/" % settings.BLOG_SLUG, include("mezzanine.blog.urls")),
    )
if "mezzanine.pages" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^", include("mezzanine.pages.urls")),
    )
if getattr(settings, "DEV_SERVER", False):
    media_root = settings.MEDIA_ROOT
    theme = getattr(settings, "THEME")
    if theme:
        media_root = os.path.join(path_for_import(theme), "media")
    urlpatterns += patterns("",
        ("^%s/(?P<path>.*)$" % settings.MEDIA_URL.strip("/"),
            "django.views.static.serve", {"document_root": media_root}),
    )
