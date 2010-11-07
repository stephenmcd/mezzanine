
from django.conf.urls.defaults import *
from django.contrib import admin

from mezzanine.conf import settings


admin.autodiscover()

urlpatterns = patterns("",
    ("^admin/", include(admin.site.urls)),
    ("^", include("mezzanine.urls")),
)

if getattr(settings, "DEV_SERVER", False):
    urlpatterns += patterns("",
        ("^%s/(?P<path>.*)$" % settings.MEDIA_URL.strip("/"),
            "django.views.static.serve",
                {"document_root": settings.MEDIA_ROOT}),
        ("^favicon.ico$", "django.views.static.serve", {"document_root":
            settings.MEDIA_ROOT, "path": "img/favicon.ico"}),
    )
