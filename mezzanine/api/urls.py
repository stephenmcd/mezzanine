from __future__ import unicode_literals
from django.conf.urls import patterns, url, include

urlpatterns = patterns("",
    ("^blog/", include("mezzanine.api.blog.urls")),
    ("^core/", include("mezzanine.api.core.urls")),
    ("^pages/", include("mezzanine.api.pages.urls")),
)
