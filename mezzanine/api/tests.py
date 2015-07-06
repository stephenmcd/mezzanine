from __future__ import unicode_literals

import json
import re

from unittest import skipUnless
from datetime import datetime

from django.core.urlresolvers import reverse

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.conf import settings
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.generic.models import AssignedKeyword
from mezzanine.generic.models import Keyword
from mezzanine.utils.tests import TestCase


@skipUnless("mezzanine.api" in settings.INSTALLED_APPS and
            "mezzanine.blog" in settings.INSTALLED_APPS,
            "api and blog app required")
class ApiBlogTest(TestCase):
    """

    .. note::
        In order to prevent `InSecurePlatformWarning` is recommended
        to use `requests==2.5.3`.
        For more information about it:
        https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

    """
    def parse_iso_datetime(self, iso_datetime):
        """
        Converts iso format datetime to datetime object.

        :param iso_datetime: iso datetime like "2008-09-03T20:56:35.450686Z"
        :rtype iso_datetime: str
        :return: datetime object.
        """
        r = re.split('[^\d]', iso_datetime)
        return datetime(*map(int, r[:-1]))

    def get_json_response(self, url):
        """
        Do request from url and returns response in json.

        :param url: url to do request
        :return: response in json.
        """
        data = self.client.get(url).content
        return json.loads(data)

    def setUp(self):
        super(ApiBlogTest, self).setUp()
        Keyword.objects.all().delete()

        category = BlogCategory.objects.create(title='Blog Category')

        blog_post_data = dict(
            title="Post",
            description="Post for test tags, category, author and month",
            user=self._user,
            status=CONTENT_STATUS_PUBLISHED,
            keywords_string=','.join(["how", "now", "brown", "cow"])
        )
        blog_post = BlogPost.objects.create(**blog_post_data)
        blog_post.categories.add(category)

        keywords = ["how", "now", "brown", "cow"]
        for keyword in keywords:
            keyword_id = Keyword.objects.get_or_create(title=keyword)[0].id
            blog_post.keywords.add(AssignedKeyword(keyword_id=keyword_id))

        blog_post.save()

        blog_post_data = dict(
            title="Post 2",
            description="Post for test tags, category, author and month",
            user=self._user,
            status=CONTENT_STATUS_PUBLISHED,
            keywords_string=','.join(["brown", "cow"])
        )
        blog_post = BlogPost.objects.create(**blog_post_data)
        blog_post.categories.add(category)

        keywords = ["brown", "cow"]
        for keyword in keywords:
            keyword_id = Keyword.objects.get_or_create(title=keyword)[0].id
            blog_post.keywords.add(AssignedKeyword(keyword_id=keyword_id))

        blog_post.save()

    def test_blog_list(self):
        data = self.get_json_response(reverse('blogpost-list'))
        post = data['results'][0]
        self.assertEqual(post['title'], 'Post 2')
        self.assertIn("brown", post['keywords_string'])
        self.assertEqual(len(post['categories']), 1)

    def test_blog_tags(self):
        data = self.get_json_response(reverse('blogpost-posts-by-tags'))
        # data:
        # [{u'count': 1, u'slug': u'how', u'title': u'how'},
        #  {u'count': 1, u'slug': u'now', u'title': u'now'},
        #  {u'count': 2, u'slug': u'brown', u'title': u'brown'},
        #  {u'count': 2, u'slug': u'cow', u'title': u'cow'}]

        keywords = {}
        for d in data:
            keywords[d['slug']] = d['count']

        self.assertEqual(keywords['how'], 1)
        self.assertEqual(keywords['brown'], 2)

    def test_blog_months(self):
        data = self.get_json_response(reverse('blogpost-posts-by-months'))
        # data: [[u'2015-07-01T00:00:00', 2]]

        self.assertGreater(len(data), 0,
                           'Should be at least one date from post')

        now = datetime.now()
        iso_datetime, count = data[0]
        iso_datetime = self.parse_iso_datetime(iso_datetime)

        self.assertEqual(iso_datetime.month, now.month)
        self.assertEqual(count, 2)

    def test_blog_authors(self):
        data = self.get_json_response(reverse('blogpost-posts-by-authors'))
        # data: [{u'count': 2, u'author': u'test'}]

        self.assertEqual(data[0]['author'], self._user.username)
        self.assertEqual(data[0]['count'], 2)

    def test_blog_categories(self):
        data = self.get_json_response(reverse('blogpost-posts-by-categories'))
        # data:
        # [{'count': 2, 'slug': 'blog-category', 'title': u'Blog Category'}]

        data = data[0]
        category = BlogCategory.objects.get(title='Blog Category')
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['title'], category.title)
