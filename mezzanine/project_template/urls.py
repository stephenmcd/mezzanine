
from django.conf.urls.defaults import *
from django.contrib import admin

from mezzanine.conf import settings
from mezzanine.utils import path_for_import


admin.autodiscover()

urlpatterns = patterns("",
    ("^admin/", include(admin.site.urls)),
    ("^", include("mezzanine.urls")),
)

if getattr(settings, "DEV_SERVER", False):
    media_root = settings.MEDIA_ROOT
    theme = getattr(settings, "THEME")
    if theme:
        media_root = path_for_import(theme)
    urlpatterns += patterns("",
        ("^%s/(?P<path>.*)$" % settings.MEDIA_URL.strip("/"),
            "django.views.static.serve", {"document_root": media_root}),
        ("^favicon.ico$", 
            "django.views.static.serve", {"document_root": media_root, 
                                          "path": "img/favicon.ico"}),
    )
