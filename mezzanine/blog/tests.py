from __future__ import unicode_literals

from unittest import skipUnless

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from django.core.urlresolvers import reverse

from mezzanine.blog.models import BlogPost
from mezzanine.conf import settings
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.pages.models import Page, RichTextPage
from mezzanine.utils.tests import TestCase


class BlogTests(TestCase):

    def test_blog_views(self):
        """
        Basic status code test for blog views.
        """
        response = self.client.get(reverse("blog_post_list"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("blog_post_feed", args=("rss",)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("blog_post_feed", args=("atom",)))
        self.assertEqual(response.status_code, 200)
        blog_post = BlogPost.objects.create(title="Post", user=self._user,
                                            status=CONTENT_STATUS_PUBLISHED)
        response = self.client.get(blog_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    @skipUnless("mezzanine.accounts" in settings.INSTALLED_APPS and
                "mezzanine.pages" in settings.INSTALLED_APPS,
                "accounts and pages apps required")
    def test_login_protected_blog(self):
        """
        Test the blog is login protected if its page has login_required
        set to True.
        """
        slug = settings.BLOG_SLUG or "/"
        RichTextPage.objects.create(title="blog", slug=slug,
                                    login_required=True)
        response = self.client.get(reverse("blog_post_list"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.redirect_chain) > 0)
        redirect_path = urlparse(response.redirect_chain[0][0]).path
        self.assertEqual(redirect_path, settings.LOGIN_URL)

    def test_blog_post_list_can_use_any_page_type(self):
        """Test that the blog post list can use any Page type."""
        slug = settings.BLOG_SLUG or "/"
        Page.objects.create(title="blog", slug=slug)
        response = self.client.get(reverse("blog_post_list"))
        self.assertEqual(response.status_code, 200)
