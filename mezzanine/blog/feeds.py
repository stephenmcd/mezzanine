
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
from mezzanine.pages.models import Page
from mezzanine.conf import settings


class PostsRSS(Feed):
    """
    RSS feed for all blog posts.
    """

    def __init__(self, *args, **kwargs):
        """
        Use the title and description of the Blog page for the feed's
        title and description. If the blog page has somehow been
        removed, fall back to the ``SITE_TITLE`` and ``SITE_TAGLINE``
        settings.
        """
        super(PostsRSS, self).__init__(*args, **kwargs)
        self._public = True
        try:
            page = Page.objects.published().get(slug=settings.BLOG_SLUG)
        except Page.DoesNotExist:
            page = None
        else:
            self._public = not page.login_required
        if self._public:
            if page is not None:
                self.title = page.title
                self.description = strip_tags(page.description)
            else:
                settings.use_editable()
                self.title = settings.SITE_TITLE
                self.description = settings.SITE_TAGLINE

    def link(self):
        return reverse("blog_post_feed", kwargs={"format": "rss"})

    def items(self):
        if not self._public:
            return []
        return BlogPost.objects.published().select_related("user")

    def item_description(self, item):
        return item.content

    def categories(self):
        if not self._public:
            return []
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
        return self.description

    def link(self):
        return reverse("blog_post_feed", kwargs={"format": "atom"})
