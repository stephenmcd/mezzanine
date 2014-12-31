from django.conf.urls import patterns, url
from .views import ThreadedCommentAPIView

urlpatterns = patterns("mezzanine.api.generic.views",
    url('^$', ThreadedCommentAPIView.as_view(), name='comments_api'),
)
