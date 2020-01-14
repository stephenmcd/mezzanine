from django.urls import re_path
from django.conf import settings

from mezzanine.pages import page_processors, views


page_processors.autodiscover()


# Page patterns.
urlpatterns = [
    re_path("(?P<slug>.*)%s$" % ("/" if settings.APPEND_SLASH else ""),
        views.page, name="page"),
]
