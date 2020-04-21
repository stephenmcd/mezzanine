from __future__ import unicode_literals

from django.conf.urls import url

from mezzanine.generic import views


urlpatterns = [
    url(r"^rating/$", views.rating, name="rating"),
    url(r"^comment/$", views.comment, name="comment"),
]
