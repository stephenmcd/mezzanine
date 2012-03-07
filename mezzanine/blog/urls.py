
from django.conf.urls.defaults import patterns, url

from mezzanine.blog.feeds import PostsRSS, PostsAtom


blog_feed_dict = {"rss": PostsRSS, "atom": PostsAtom}
try:
    # Django <= 1.3
    from django.contrib.syndication.views import feed
    blog_feed_dict = {"feed_dict": blog_feed_dict}
except ImportError:
    # Django >= 1.4
    feed = lambda request, url, **kwargs: kwargs[url]()(request)

# Blog feed patterns.
urlpatterns = patterns("",
    url("^feeds/(?P<url>.*)/$", feed, blog_feed_dict, name="blog_post_feed"),
)

# Blog patterns.
urlpatterns += patterns("mezzanine.blog.views",
    url("^tag/(?P<tag>.*)/$", "blog_post_list", name="blog_post_list_tag"),
    url("^category/(?P<category>.*)/$", "blog_post_list",
        name="blog_post_list_category"),
    url("^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$", "blog_post_list",
        name="blog_post_list_month"),
    url("^author/(?P<username>.*)/$", "blog_post_list",
        name="blog_post_list_author"),
    url("^archive/(?P<year>.*)/$", "blog_post_list",
        name="blog_post_list_year"),
    url("^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>.*)/$",
        "blog_post_detail", name="blog_post_detail_date"),
    url("^(?P<slug>.*)/$", "blog_post_detail", name="blog_post_detail"),
    url("^$", "blog_post_list", name="blog_post_list"),
)
