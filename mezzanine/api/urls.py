from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import PagesAPIView

urlpatterns = []

urlpatterns += patterns("mezzanine.api.views",
    url('^pages/$', PagesAPIView.as_view(), name='pages_api'),
)
