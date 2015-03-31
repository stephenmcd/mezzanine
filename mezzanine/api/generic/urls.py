from django.conf.urls import patterns
from django.conf.urls import url
from .views import ThreadedCommentAPIView

urls = [
    url('^$', ThreadedCommentAPIView.as_view(), name='comments_api'),
]

urlpatterns = patterns("mezzanine.api.generic.views", urls)
