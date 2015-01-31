from django.conf.urls import patterns, url
from .views import PagesAPIView, RichTextPageAPIView

urlpatterns = patterns("mezzanine.api.pages.views",
    url('^page$', PagesAPIView.as_view()),
    url('^richtextpage$', RichTextPageAPIView.as_view()),
)
