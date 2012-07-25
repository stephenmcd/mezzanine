
from django.conf.urls.defaults import patterns, url

from mezzanine.conf import settings


urlpatterns = []

if "django.contrib.admin" in settings.INSTALLED_APPS:
    urlpatterns += patterns("django.contrib.auth.views",
        url("^password_reset/$", "password_reset", name="password_reset"),
        ("^password_reset/done/$", "password_reset_done"),
        ("^reset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$",
            "password_reset_confirm"),
        ("^reset/done/$", "password_reset_complete"),
    )

_proxy_url = getattr(settings, "STATIC_PROXY_URL", "static_proxy").strip("/")

urlpatterns += patterns("mezzanine.core.views",
    url("^edit/$", "edit", name="edit"),
    url("^search/$", "search", name="search"),
    url("^set_site/$", "set_site", name="set_site"),
    url("^set_device/(?P<device>.*)/$", "set_device", name="set_device"),
    url("^%s/$" % _proxy_url, "static_proxy", name="static_proxy"),
)
