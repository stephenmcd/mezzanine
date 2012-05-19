
from django.conf.urls.defaults import patterns, url

from mezzanine.conf import settings


SIGNUP_URL = getattr(settings, "SIGNUP_URL", "/account/signup/")
SIGNUP_VERIFY_URL = getattr(settings, "SIGNUP_VERIFY_URL", "/account/verify/")
LOGIN_URL = settings.LOGIN_URL
LOGOUT_URL = settings.LOGOUT_URL
PROFILE_URL = getattr(settings, "PROFILE_URL", "/users/")
PROFILE_UPDATE_URL = getattr(settings, "PROFILE_UPDATE_URL",
                             "/account/update/")
PASSWORD_RESET_URL = getattr(settings, "PASSWORD_RESET_URL",
                             "/account/password/reset/")
PASSWORD_RESET_VERIFY_URL = getattr(settings, "PASSWORD_RESET_VERIFY_URL",
                                    "/account/password/verify/")

verify_pattern = "/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$"

urlpatterns = patterns("mezzanine.accounts.views",
    url("^%s/$" % LOGIN_URL.strip("/"), "login", name="login"),
    url("^%s/$" % LOGOUT_URL.strip("/"), "logout", name="logout"),
    url("^%s/$" % SIGNUP_URL.strip("/"), "signup", name="signup"),
    url("^%s%s" % (SIGNUP_VERIFY_URL.strip("/"), verify_pattern),
        "signup_verify", name="signup_verify"),
    url("^%s/$" % PROFILE_UPDATE_URL.strip("/"), "profile_update",
        name="profile_update"),
    url("^%s/$" % PASSWORD_RESET_URL.strip("/"), "password_reset",
        name="mezzanine_password_reset"),
    url("^%s%s" % (PASSWORD_RESET_VERIFY_URL.strip("/"), verify_pattern),
        "password_reset_verify", name="password_reset_verify"),
)

if settings.ACCOUNTS_PROFILE_VIEWS_ENABLED:
    urlpatterns += patterns("mezzanine.accounts.views",
        url("^%s/(?P<username>.*)/$" % PROFILE_URL.strip("/"), "profile",
            name="profile"),
    )
