from __future__ import division, unicode_literals
from future.utils import native_str

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.unittest import skipUnless

from mezzanine.blog.models import BlogPost
from mezzanine.conf import settings

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.generic.forms import RatingForm
from mezzanine.generic.models import (AssignedKeyword, Keyword,
                                      ThreadedComment, Rating)
from mezzanine.pages.models import RichTextPage
from mezzanine.utils.tests import TestCase


class GenericTests(TestCase):

    @skipUnless("mezzanine.blog" in settings.INSTALLED_APPS,
                "blog app required")
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
            # Django doesn't seem to support unicode cookie keys correctly on
            # Python 2. See https://code.djangoproject.com/ticket/19802
            response.delete_cookie(native_str("mezzanine-rating"))
        blog_post = BlogPost.objects.get(id=blog_post.id)
        count = len(settings.RATINGS_RANGE)
        _sum = sum(settings.RATINGS_RANGE)
        average = _sum / count
        self.assertEqual(blog_post.rating_count, count)
        self.assertEqual(blog_post.rating_sum, _sum)
        self.assertEqual(blog_post.rating_average, average)

    @skipUnless("mezzanine.blog" in settings.INSTALLED_APPS,
                "blog app required")
    def test_comment_ratings(self):
        """
        Test that a generic relation defined on one of Mezzanine's generic
        models (in this case ratings of comments) correctly sets its
        extra fields.
        """
        blog_post = BlogPost.objects.create(title="Post with comments",
                                            user=self._user)
        content_type = ContentType.objects.get_for_model(blog_post)
        kwargs = {"content_type": content_type, "object_pk": blog_post.id,
                  "site_id": settings.SITE_ID, "comment": "First!!!11"}
        comment = ThreadedComment.objects.create(**kwargs)
        comment.rating.create(value=3)
        comment.rating.add(Rating(value=5))
        comment = ThreadedComment.objects.get(pk=comment.pk)

        self.assertEqual(len(comment.rating.all()), comment.rating_count)

        self.assertEqual(comment.rating_average, 4)

    @skipUnless("mezzanine.blog" in settings.INSTALLED_APPS,
                "blog app required")
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
        self.assertEqual(before, after)

    @skipUnless("mezzanine.pages" in settings.INSTALLED_APPS,
                "pages app required")
    def test_keywords(self):
        """
        Test that the keywords_string field is correctly populated.
        """
        page = RichTextPage.objects.create(title="test keywords")
        keywords = set(["how", "now", "brown", "cow"])
        Keyword.objects.all().delete()
        for keyword in keywords:
            keyword_id = Keyword.objects.get_or_create(title=keyword)[0].id
            page.keywords.add(AssignedKeyword(keyword_id=keyword_id))
        page = RichTextPage.objects.get(id=page.id)
        self.assertEqual(keywords, set(page.keywords_string.split()))
        # Test removal.
        first = Keyword.objects.all()[0]
        keywords.remove(first.title)
        first.delete()
        page = RichTextPage.objects.get(id=page.id)
        self.assertEqual(keywords, set(page.keywords_string.split()))
        page.delete()
