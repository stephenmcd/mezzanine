from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mezzanine.conf import settings


urlpatterns = []

if "django.contrib.admin" in settings.INSTALLED_APPS:
    from django import VERSION
    if VERSION < (1, 6):
        reset_pattern = "^reset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$"
    else:
        reset_pattern = "^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$"
    urlpatterns += patterns("django.contrib.auth.views",
        url("^password_reset/$", "password_reset", name="password_reset"),
        url("^password_reset/done/$", "password_reset_done",
            name="password_reset_done"),
        url("^reset/done/$", "password_reset_complete",
            name="password_reset_complete"),
        url(reset_pattern, "password_reset_confirm",
            name="password_reset_confirm"),
    )

urlpatterns += patterns("mezzanine.core.views",
    url("^edit/$", "edit", name="edit"),
    url("^search/$", "search", name="search"),
    url("^set_site/$", "set_site", name="set_site"),
    url("^set_device/(?P<device>.*)/$", "set_device", name="set_device"),
    url("^asset_proxy/$", "static_proxy", name="static_proxy"),
    url("^displayable_links.js$", "displayable_links_js",
        name="displayable_links_js"),
)
