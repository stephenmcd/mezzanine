from django.conf.urls import url

from mezzanine.accounts import views
from mezzanine.conf import settings


ACCOUNT_URL = getattr(settings, "ACCOUNT_URL", "/accounts/")
SIGNUP_URL = getattr(settings, "SIGNUP_URL", "/%s/signup/" % ACCOUNT_URL.strip("/"))
SIGNUP_VERIFY_URL = getattr(
    settings, "SIGNUP_VERIFY_URL", "/%s/verify/" % ACCOUNT_URL.strip("/")
)
LOGIN_URL = settings.LOGIN_URL
LOGOUT_URL = getattr(settings, "LOGOUT_URL", "/%s/logout/" % ACCOUNT_URL.strip("/"))

PROFILE_URL = getattr(settings, "PROFILE_URL", "/users/")
PROFILE_UPDATE_URL = getattr(
    settings, "PROFILE_UPDATE_URL", "/%s/update/" % ACCOUNT_URL.strip("/")
)
PASSWORD_RESET_URL = getattr(
    settings, "PASSWORD_RESET_URL", "/%s/password/reset/" % ACCOUNT_URL.strip("/")
)
PASSWORD_RESET_VERIFY_URL = getattr(
    settings,
    "PASSWORD_RESET_VERIFY_URL",
    "/%s/password/verify/" % ACCOUNT_URL.strip("/"),
)

_verify_pattern = r"/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)"
_slash = "/" if settings.APPEND_SLASH else ""

urlpatterns = [
    url(r"^%s%s$" % (LOGIN_URL.strip("/"), _slash), views.login, name="login"),
    url(r"^%s%s$" % (LOGOUT_URL.strip("/"), _slash), views.logout, name="logout"),
    url(r"^%s%s$" % (SIGNUP_URL.strip("/"), _slash), views.signup, name="signup"),
    url(
        r"^%s%s%s$" % (SIGNUP_VERIFY_URL.strip("/"), _verify_pattern, _slash),
        views.signup_verify,
        name="signup_verify",
    ),
    url(
        r"^%s%s$" % (PROFILE_UPDATE_URL.strip("/"), _slash),
        views.profile_update,
        name="profile_update",
    ),
    url(
        r"^%s%s$" % (PASSWORD_RESET_URL.strip("/"), _slash),
        views.password_reset,
        name="mezzanine_password_reset",
    ),
    url(
        r"^%s%s%s$" % (PASSWORD_RESET_VERIFY_URL.strip("/"), _verify_pattern, _slash),
        views.password_reset_verify,
        name="password_reset_verify",
    ),
    url(
        r"^%s%s$" % (ACCOUNT_URL.strip("/"), _slash),
        views.account_redirect,
        name="account_redirect",
    ),
]

if settings.ACCOUNTS_PROFILE_VIEWS_ENABLED:
    urlpatterns += [
        url(
            r"^%s%s$" % (PROFILE_URL.strip("/"), _slash),
            views.profile_redirect,
            name="profile_redirect",
        ),
        url(
            r"^%s/(?P<username>.*)%s$" % (PROFILE_URL.strip("/"), _slash),
            views.profile,
            name="profile",
        ),
    ]
