from django.conf.urls import patterns, url
from .views import PagesAPIView

urlpatterns = patterns("mezzanine.api.pages.views",
    url('^pages$', PagesAPIView.as_view(), name='pages_api'),
)
