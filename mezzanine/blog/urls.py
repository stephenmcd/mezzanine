from django.urls import re_path

from mezzanine.blog import views
from mezzanine.conf import settings


# Trailing slahes for urlpatterns based on setup.
_slash = "/" if settings.APPEND_SLASH else ""

# Blog patterns.
urlpatterns = [
    re_path(
        r"^feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed,
        name="blog_post_feed",
    ),
    re_path(
        r"^tag/(?P<tag>.*)/feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed,
        name="blog_post_feed_tag",
    ),
    re_path(
        r"^tag/(?P<tag>.*)%s$" % _slash, views.blog_post_list, name="blog_post_list_tag"
    ),
    re_path(
        r"^category/(?P<category>.*)/feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed,
        name="blog_post_feed_category",
    ),
    re_path(
        r"^category/(?P<category>.*)%s$" % _slash,
        views.blog_post_list,
        name="blog_post_list_category",
    ),
    re_path(
        r"^author/(?P<username>.*)/feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed,
        name="blog_post_feed_author",
    ),
    re_path(
        r"^author/(?P<username>.*)%s$" % _slash,
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
    re_path(
        r"^(?P<slug>.*)%s$" % _slash, views.blog_post_detail, name="blog_post_detail"
    ),
    re_path(r"^$", views.blog_post_list, name="blog_post_list"),
]
