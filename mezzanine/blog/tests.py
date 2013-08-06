
from urlparse import urlparse

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import connection
from django.template import Context, Template
from django.test import TestCase

from mezzanine.blog.models import BlogPost
from mezzanine.conf import settings

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.generic.forms import RatingForm
from mezzanine.generic.models import ThreadedComment
from mezzanine.pages.models import RichTextPage
from mezzanine.utils.models import get_user_model


User = get_user_model()


class TestsBlogPost(TestCase):

    def setUp(self):
        self._username = "test"
        self._password = "test"
        args = (self._username, "example@example.com", self._password)
        self._user = User.objects.create_superuser(*args)

    def queries_used_for_template(self, template, **context):
        """
        Return the number of queries used when rendering a template string.
        """
        connection.queries = []
        t = Template(template)
        t.render(Context(context))
        return len(connection.queries)

    def create_recursive_objects(self, model, parent_field, **kwargs):
        """
        Create multiple levels of recursive objects.
        """
        per_level = range(3)
        for _ in per_level:
            kwargs[parent_field] = None
            level1 = model.objects.create(**kwargs)
            for _ in per_level:
                kwargs[parent_field] = level1
                level2 = model.objects.create(**kwargs)
                for _ in per_level:
                    kwargs[parent_field] = level2
                    model.objects.create(**kwargs)

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
        # Test the blog is login protected if its page has login_required
        # set to True.
        slug = settings.BLOG_SLUG or "/"
        RichTextPage.objects.create(title="blog", slug=slug,
                                    login_required=True)
        response = self.client.get(reverse("blog_post_list"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.redirect_chain) > 0)
        redirect_path = urlparse(response.redirect_chain[0][0]).path
        self.assertEqual(redirect_path, settings.LOGIN_URL)

    def test_rating(self):
        """
        Test that ratings can be posted and avarage/count are calculated.
        """
        blog_post = BlogPost.objects.create(title="Ratings", user=self._user,
                                            status=CONTENT_STATUS_PUBLISHED)
        data = RatingForm(None, blog_post).initial
        for value in settings.RATINGS_RANGE:
            data["value"] = value
            response = self.client.post(reverse("rating"), data=data)
            response.delete_cookie("mezzanine-rating")
        blog_post = BlogPost.objects.get(id=blog_post.id)
        count = len(settings.RATINGS_RANGE)
        _sum = sum(settings.RATINGS_RANGE)
        average = _sum / float(count)
        self.assertEqual(blog_post.rating_count, count)
        self.assertEqual(blog_post.rating_sum, _sum)
        self.assertEqual(blog_post.rating_average, average)

    def test_comment_queries(self):
        """
        Test that rendering comments executes the same number of
        queries, regardless of the number of nested replies.
        """
        blog_post = BlogPost.objects.create(title="Post", user=self._user)
        content_type = ContentType.objects.get_for_model(blog_post)
        kwargs = {"content_type": content_type, "object_pk": blog_post.id,
                  "site_id": settings.SITE_ID}
        template = "{% load comment_tags %}{% comment_thread blog_post %}"
        context = {
            "blog_post": blog_post,
            "posted_comment_form": None,
            "unposted_comment_form": None,
        }
        before = self.queries_used_for_template(template, **context)
        self.assertTrue(before > 0)
        self.create_recursive_objects(ThreadedComment, "replied_to", **kwargs)
        after = self.queries_used_for_template(template, **context)
        self.assertEquals(before, after)
