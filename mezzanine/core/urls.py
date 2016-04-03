from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from mezzanine.conf import settings
from mezzanine.core import views as core_views


urlpatterns = []

if "django.contrib.admin" in settings.INSTALLED_APPS:
    urlpatterns += [
        url("^password_reset/$", auth_views.password_reset,
            name="password_reset"),
        url("^password_reset/done/$", auth_views.password_reset_done,
            name="password_reset_done"),
        url("^reset/done/$", auth_views.password_reset_complete,
            name="password_reset_complete"),
        url("^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
            auth_views.password_reset_confirm, name="password_reset_confirm"),
    ]

urlpatterns += [
    url("^edit/$", core_views.edit, name="edit"),
    url("^search/$", core_views.search, name="search"),
    url("^set_site/$", core_views.set_site, name="set_site"),
    url("^set_device/(?P<device>.*)/$", core_views.set_device,
        name="set_device"),
]
