
try:
    # Django <= 1.3
    from django.contrib.syndication.feeds import Feed
except ImportError:
    # Django >= 1.4
    from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from django.utils.html import strip_tags

from mezzanine.blog.models import BlogPost, BlogCategory
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
        return BlogPost.objects.published().select_related("user")

    def categories(self):
        return BlogCategory.objects.all()

    def item_author_name(self, item):
        return item.user.get_full_name() or item.user.username

    def item_author_link(self, item):
        username = item.user.username
        return reverse("blog_post_list_author", kwargs={"username": username})

    def item_pubdate(self, item):
        return item.publish_date

    def item_categories(self, item):
        return item.categories.all()


class PostsAtom(PostsRSS):
    """
    Atom feed for all blog posts.
    """

    feed_type = Atom1Feed

    def subtitle(self):
        return self.description()

    def link(self):
        return reverse("blog_post_feed", kwargs={"url": "atom"})
