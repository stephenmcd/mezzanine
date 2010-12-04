
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from django.utils.html import strip_tags

from mezzanine.blog.models import BlogPost
from mezzanine.blog.views import blog_page


class PostsRSS(Feed):
    """
    RSS feed for all blog posts.
    """

    def title(self):
        return blog_page().title

    def description(self):
        return strip_tags(blog_page().description)

    def link(self):
        return reverse("blog_post_feed", kwargs={"url": "rss"})

    def items(self):
        return BlogPost.objects.published()


class PostsAtom(PostsRSS):
    """
    Atom feed for all blog posts.
    """

    feed_type = Atom1Feed

    def subtitle(self):
        return self.description()

    def link(self):
        return reverse("blog_post_feed", kwargs={"url": "atom"})
