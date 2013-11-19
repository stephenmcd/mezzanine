from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("mezzanine.generic.views",
    url("^admin_keywords_submit/$", "admin_keywords_submit",
        name="admin_keywords_submit"),
    url("^rating/$", "rating", name="rating"),
    url("^comment/$", "comment", name="comment"),
)
