from django.conf.urls import patterns, url
from .views import UserAPIView

urlpatterns = patterns("mezzanine.api.core.views",
                       url('^user$', UserAPIView.as_view(), name='user_api'),
                       )
