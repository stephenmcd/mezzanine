from __future__ import division, unicode_literals

from django.template import Context
from django.template import Template
from future.utils import native_str

from unittest import skipUnless

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from mezzanine.blog.models import BlogPost
from mezzanine.conf import settings

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.generic.forms import RatingForm
from mezzanine.generic.models import AssignedKeyword, Keyword, ThreadedComment
from mezzanine.generic.views import comment
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
        if settings.RATINGS_ACCOUNT_REQUIRED:
            self.client.login(username=self._username, password=self._password)
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
        if settings.RATINGS_ACCOUNT_REQUIRED:
            self.assertEqual(blog_post.rating_count, 1)
            self.assertEqual(blog_post.rating_sum,
                             settings.RATINGS_RANGE[-1])
            self.assertEqual(blog_post.rating_average,
                             settings.RATINGS_RANGE[-1] / 1)
        else:
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
        comment.rating.create(value=settings.RATINGS_RANGE[0])
        comment.rating.create(value=settings.RATINGS_RANGE[-1])
        comment = ThreadedComment.objects.get(pk=comment.pk)

        self.assertEqual(len(comment.rating.all()), comment.rating_count)

        self.assertEqual(
            comment.rating_average,
            (settings.RATINGS_RANGE[0] + settings.RATINGS_RANGE[-1]) / 2)

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
        if settings.COMMENTS_ACCOUNT_REQUIRED:
            self.queries_used_for_template(template, **context)
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
            page.keywords.get_or_create(keyword_id=keyword_id)
        page = RichTextPage.objects.get(id=page.id)
        self.assertEqual(keywords, set(page.keywords_string.split()))
        # Test removal.
        first = Keyword.objects.all()[0]
        keywords.remove(first.title)
        first.delete()
        page = RichTextPage.objects.get(id=page.id)
        self.assertEqual(keywords, set(page.keywords_string.split()))
        page.delete()

    def test_delete_unused(self):
        """
        Only ``Keyword`` instances without any assignments should be deleted.
        """
        assigned_keyword = Keyword.objects.create(title="assigned")
        Keyword.objects.create(title="unassigned")
        AssignedKeyword.objects.create(keyword_id=assigned_keyword.id,
                                       content_object=RichTextPage(pk=1))
        Keyword.objects.delete_unused(keyword_ids=[assigned_keyword.id])
        self.assertEqual(Keyword.objects.count(), 2)
        Keyword.objects.delete_unused()
        self.assertEqual(Keyword.objects.count(), 1)
        self.assertEqual(Keyword.objects.all()[0].id, assigned_keyword.id)

    def test_comment_form_returns_400_when_missing_data(self):
        """
        Assert 400 status code response when expected data is missing from
        the comment form. This simulates typical malicious bot behavior.
        """
        request = self._request_factory.post(reverse('comment'))
        if settings.COMMENTS_ACCOUNT_REQUIRED:
            request.user = self._user
            request.session = {}
        response = comment(request)
        self.assertEquals(response.status_code, 400)

    def test_multiple_comment_forms(self):

        template = Template("""
            {% load comment_tags %}
            {% comments_for post1 %}
            {% comments_for post2 %}
        """)

        request = self._request_factory.get(reverse('comment'))
        request.user = self._user

        context = {
            'post1': BlogPost.objects.create(title="Post #1", user=self._user),
            'post2': BlogPost.objects.create(title="Post #2", user=self._user),
            'request': request,
        }

        result = template.render(Context(context))

        self.assertIn(
            '<input id="id_object_pk" name="object_pk" '
            'type="hidden" value="%d" />' % context['post2'].pk,
            result
        )
