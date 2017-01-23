from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed, add_domain
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.utils.html import strip_tags

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.conf import settings
from mezzanine.core.templatetags.mezzanine_tags import richtext_filters
from mezzanine.core.request import current_request
from mezzanine.generic.models import Keyword
from mezzanine.utils.html import absolute_urls
from mezzanine.utils.sites import current_site_id


User = get_user_model()

try:
    unicode
except NameError:  # Python 3
    unicode = lambda s: s


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
        self.tag = kwargs.pop("tag", None)
        self.category = kwargs.pop("category", None)
        self.username = kwargs.pop("username", None)
        super(PostsRSS, self).__init__(*args, **kwargs)
        self._public = True
        page = None
        if "mezzanine.pages" in settings.INSTALLED_APPS:
            from mezzanine.pages.models import Page
            try:
                page = Page.objects.published().get(slug=settings.BLOG_SLUG)
            except Page.DoesNotExist:
                pass
            else:
                self._public = not page.login_required
        if self._public:
            if page is not None:
                self._title = "%s | %s" % (page.title, settings.SITE_TITLE)
                self._description = strip_tags(page.description)
            else:
                self._title = settings.SITE_TITLE
                self._description = settings.SITE_TAGLINE

    def __call__(self, *args, **kwarg):
        self._request = current_request()
        self._site = Site.objects.get(id=current_site_id())
        return super(PostsRSS, self).__call__(*args, **kwarg)

    def add_domain(self, link):
        return add_domain(self._site.domain, link, self._request.is_secure())

    def title(self):
        return unicode(self._title)

    def description(self):
        return unicode(self._description)

    def link(self):
        return self.add_domain(reverse("blog_post_list"))

    def items(self):
        if not self._public:
            return []
        blog_posts = BlogPost.objects.published().select_related("user"
            ).prefetch_related("categories")
        if self.tag:
            tag = get_object_or_404(Keyword, slug=self.tag)
            blog_posts = blog_posts.filter(keywords__keyword=tag)
        if self.category:
            category = get_object_or_404(BlogCategory, slug=self.category)
            blog_posts = blog_posts.filter(categories=category)
        if self.username:
            author = get_object_or_404(User, username=self.username)
            blog_posts = blog_posts.filter(user=author)
        limit = settings.BLOG_RSS_LIMIT
        if limit is not None:
            blog_posts = blog_posts[:settings.BLOG_RSS_LIMIT]
        return blog_posts

    def item_description(self, item):
        description = richtext_filters(item.content)
        absolute_urls_name = "mezzanine.utils.html.absolute_urls"
        if absolute_urls_name not in settings.RICHTEXT_FILTERS:
            description = absolute_urls(description)
        return unicode(description)

    def categories(self):
        if not self._public:
            return []
        return BlogCategory.objects.all()

    def feed_url(self):
        return self.add_domain(self._request.path)

    def item_link(self, item):
        return self.add_domain(super(PostsRSS, self).item_link(item))

    def item_author_name(self, item):
        return item.user.get_full_name() or item.user.username

    def item_author_link(self, item):
        username = item.user.username
        link = reverse("blog_post_list_author", kwargs={"username": username})
        return self.add_domain(link)

    def item_pubdate(self, item):
        return item.publish_date

    def item_categories(self, item):
        return item.categories.all()

    def item_enclosure_url(self, item):
        if item.featured_image:
            return self.add_domain(item.featured_image.url)

    def item_enclosure_length(self, item):
        if item.featured_image:
            return item.featured_image.size

    def item_enclosure_mime_type(self, item):
        if item.featured_image:
            return item.featured_image.mimetype[0]


class PostsAtom(PostsRSS):
    """
    Atom feed for all blog posts.
    """

    feed_type = Atom1Feed

    def subtitle(self):
        return self.description()

    def item_updateddate(self, item):
        return item.updated
