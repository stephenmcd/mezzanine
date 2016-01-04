from __future__ import unicode_literals

from django.conf.urls import url
from django.conf import settings

from mezzanine.pages import page_processors, views


page_processors.autodiscover()

# Page patterns.
urlpatterns = [
    url("^admin_page_ordering/$", views.admin_page_ordering,
        name="admin_page_ordering"),
    url("^(?P<slug>.*)%s$" % ("/" if settings.APPEND_SLASH else ""),
        views.page, name="page"),
]
