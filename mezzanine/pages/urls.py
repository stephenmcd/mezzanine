from __future__ import unicode_literals

from django.conf.urls import url
from django.conf import settings

from mezzanine.pages import page_processors, views


page_processors.autodiscover()


# Page patterns.
urlpatterns = [
    url("^(?P<slug>.*)%s$" % ("/" if settings.APPEND_SLASH else ""),
        views.page, name="page"),
]
