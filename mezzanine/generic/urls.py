from django.urls import path

from mezzanine.generic import views

urlpatterns = [
    path("rating/", views.rating, name="rating"),
    path("comment/", views.comment, name="comment"),
]
