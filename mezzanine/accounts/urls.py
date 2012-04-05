
from django.conf.urls.defaults import patterns, url

from mezzanine.conf import settings


urlpatterns = patterns("mezzanine.accounts.views",
    url("^%s$" % settings.LOGIN_URL.lstrip("/"), "account",
        name="account"),
    url("^%s$" % settings.LOGOUT_URL.lstrip("/"), "logout",
        name="logout"),
    url("^verify_account/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$",
        "verify_account", name="verify_account"),
)
