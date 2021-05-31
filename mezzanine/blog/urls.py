from django.urls import path, re_path

from mezzanine.blog import views
from mezzanine.conf import settings

# Trailing slahes for urlpatterns based on setup.
_slash = "/" if settings.APPEND_SLASH else ""

# Blog patterns.
urlpatterns = [
    path(
        "feeds/<format>" + _slash,
        views.blog_post_feed,
        name="blog_post_feed",
    ),
    path(
        "tag/<tag>/feeds/<format>" + _slash,
        views.blog_post_feed,
        name="blog_post_feed_tag",
    ),
    path("tag/<tag>" + _slash, views.blog_post_list, name="blog_post_list_tag"),
    path(
        "category/<category>/feeds/<format>" + _slash,
        views.blog_post_feed,
        name="blog_post_feed_category",
    ),
    path(
        "category/<category>" + _slash,
        views.blog_post_list,
        name="blog_post_list_category",
    ),
    path(
        "author/<username>/feeds/<format>" + _slash,
        views.blog_post_feed,
        name="blog_post_feed_author",
    ),
    path(
        "author/<username>" + _slash,
        views.blog_post_list,
        name="blog_post_list_author",
    ),
    re_path(
        r"^archive/(?P<year>\d{4})/(?P<month>\d{1,2})%s$" % _slash,
        views.blog_post_list,
        name="blog_post_list_month",
    ),
    re_path(
        r"^archive/(?P<year>\d{4})%s$" % _slash,
        views.blog_post_list,
        name="blog_post_list_year",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/"
        "(?P<slug>.*)%s$" % _slash,
        views.blog_post_detail,
        name="blog_post_detail_day",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>.*)%s$" % _slash,
        views.blog_post_detail,
        name="blog_post_detail_month",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<slug>.*)%s$" % _slash,
        views.blog_post_detail,
        name="blog_post_detail_year",
    ),
    path("<slug>" + _slash, views.blog_post_detail, name="blog_post_detail"),
    path("", views.blog_post_list, name="blog_post_list"),
]
