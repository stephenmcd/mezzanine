from __future__ import unicode_literals
from django.conf.urls import patterns, include

urls = [
    ("^blog/", include("mezzanine.api.blog.urls")),
    ("^pages/", include("mezzanine.api.pages.urls")),
    ("^generic/", include("mezzanine.api.generic.urls")),
]

urlpatterns = patterns("", urls)
