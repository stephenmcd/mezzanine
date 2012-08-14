
from django.conf.urls.defaults import patterns, url


# Blog patterns.
urlpatterns = patterns("mezzanine.blog.views",
    url("^feeds/(?P<format>.*)/$", "blog_post_feed", name="blog_post_feed"),
    url("^tag/(?P<tag>.*)/feeds/(?P<format>.*)/$", "blog_post_feed",
        name="blog_post_feed_tag"),
    url("^tag/(?P<tag>.*)/$", "blog_post_list", name="blog_post_list_tag"),
    url("^category/(?P<category>.*)/feeds/(?P<format>.*)/$", "blog_post_feed",
        name="blog_post_feed_category"),
    url("^category/(?P<category>.*)/$", "blog_post_list",
        name="blog_post_list_category"),
    url("^author/(?P<username>.*)/feeds/(?P<format>.*)/$", "blog_post_feed",
        name="blog_post_feed_author"),
    url("^author/(?P<username>.*)/$", "blog_post_list",
        name="blog_post_list_author"),
    url("^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$", "blog_post_list",
        name="blog_post_list_month"),
    url("^archive/(?P<year>.*)/$", "blog_post_list",
        name="blog_post_list_year"),
    url("^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>.*)/$",
        "blog_post_detail", name="blog_post_detail_date"),
    url("^(?P<slug>.*)/$", "blog_post_detail", name="blog_post_detail"),
    url("^$", "blog_post_list", name="blog_post_list"),
)
