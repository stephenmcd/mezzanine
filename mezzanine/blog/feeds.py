
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed

from mezzanine.blog.models import BlogPost
from mezzanine.settings import BLOG_TITLE, BLOG_DESCRIPTION


class PostsRSS(Feed):
    """
    RSS feed for all blog posts.
    """

    title = BLOG_TITLE
    description = BLOG_DESCRIPTION
    
    def link(self):
        return reverse("blog_post_feed", kwargs={"url": "rss"})
    
    def items(self):
        return BlogPost.objects.published()

class PostsAtom(PostsRSS):
    """
    Atom feed for all blog posts.
    """
    
    feed_type = Atom1Feed
    subtitle = PostsRSS.description

    def link(self):
        return reverse("blog_post_feed", kwargs={"url": "atom"})

