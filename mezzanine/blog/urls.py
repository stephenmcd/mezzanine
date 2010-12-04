
from django.conf.urls.defaults import *

from mezzanine.blog.feeds import PostsRSS, PostsAtom


# Blog feed patterns.
blog_feed_dict = {"rss": PostsRSS, "atom": PostsAtom}
urlpatterns = patterns("",
    url("^feeds/(?P<url>.*)/$", "django.contrib.syndication.views.feed",
        {"feed_dict": blog_feed_dict}, name="blog_post_feed"),
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
    url("^(?P<slug>.*)/$", "blog_post_detail", name="blog_post_detail"),
    url("^$", "blog_post_list", name="blog_post_list"),
)
