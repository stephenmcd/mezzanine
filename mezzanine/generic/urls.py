from __future__ import unicode_literals

from django.conf.urls import url

from mezzanine.generic import views


urlpatterns = [
    url("^admin_keywords_submit/$", views.admin_keywords_submit,
        name="admin_keywords_submit"),
    url("^rating/$", views.rating, name="rating"),
    url("^comment/$", views.comment, name="comment"),
]
