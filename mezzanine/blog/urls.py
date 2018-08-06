from __future__ import unicode_literals

from django.conf.urls import url

from mezzanine.blog import views
from mezzanine.conf import settings


# Trailing slahes for urlpatterns based on setup.
_slash = "/" if settings.APPEND_SLASH else ""

# Blog patterns.
urlpatterns = [
    url(r"^feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed, name="blog_post_feed"),
    url(r"^tag/(?P<tag>.*)/feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed, name="blog_post_feed_tag"),
    url(r"^tag/(?P<tag>.*)%s$" % _slash,
        views.blog_post_list, name="blog_post_list_tag"),
    url(r"^category/(?P<category>.*)/feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed, name="blog_post_feed_category"),
    url(r"^category/(?P<category>.*)%s$" % _slash,
        views.blog_post_list, name="blog_post_list_category"),
    url(r"^author/(?P<username>.*)/feeds/(?P<format>.*)%s$" % _slash,
        views.blog_post_feed, name="blog_post_feed_author"),
    url(r"^author/(?P<username>.*)%s$" % _slash,
        views.blog_post_list, name="blog_post_list_author"),
    url(r"^archive/(?P<year>\d{4})/(?P<month>\d{1,2})%s$" % _slash,
        views.blog_post_list, name="blog_post_list_month"),
    url(r"^archive/(?P<year>\d{4})%s$" % _slash,
        views.blog_post_list, name="blog_post_list_year"),
    url(r"^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/"
        "(?P<slug>.*)%s$" % _slash,
        views.blog_post_detail, name="blog_post_detail_day"),
    url(r"^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>.*)%s$" % _slash,
        views.blog_post_detail, name="blog_post_detail_month"),
    url(r"^(?P<year>\d{4})/(?P<slug>.*)%s$" % _slash,
        views.blog_post_detail, name="blog_post_detail_year"),
    url(r"^(?P<slug>.*)%s$" % _slash,
        views.blog_post_detail, name="blog_post_detail"),
    url(r"^$", views.blog_post_list, name="blog_post_list"),
]
