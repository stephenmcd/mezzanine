from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.conf import settings

from mezzanine.pages import page_processors

page_processors.autodiscover()


# Page patterns.
urlpatterns = patterns("mezzanine.pages.views",
    url("^admin_page_ordering/$", "admin_page_ordering",
        name="admin_page_ordering"),
    url("^(?P<slug>.*)%s$" % ("/" if settings.APPEND_SLASH else ""),
        "page", name="page"),
)
