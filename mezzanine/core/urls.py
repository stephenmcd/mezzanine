from django.contrib.auth import views as auth_views
from django.urls import path

from mezzanine.conf import settings
from mezzanine.core import views as core_views

urlpatterns = []

if "django.contrib.admin" in settings.INSTALLED_APPS:
    urlpatterns += [
        path(
            "password_reset/",
            auth_views.PasswordResetView.as_view(),
            name="password_reset",
        ),
        path(
            "password_reset/done/",
            auth_views.PasswordResetDoneView.as_view(),
            name="password_reset_done",
        ),
        path(
            "reset/done/",
            auth_views.PasswordResetCompleteView.as_view(),
            name="password_reset_complete",
        ),
        path(
            "reset/<uidb64>/<token>/",
            auth_views.PasswordResetConfirmView.as_view(),
            name="password_reset_confirm",
        ),
    ]

urlpatterns += [
    path("edit/", core_views.edit, name="edit"),
    path("search/", core_views.search, name="search"),
    path("set_site/", core_views.set_site, name="set_site"),
]
