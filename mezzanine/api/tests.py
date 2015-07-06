from __future__ import unicode_literals

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

    def parse_iso_datetime(self, iso_datetime):
        r = re.split('[^\d]', iso_datetime)
        return datetime(*map(int, r[:-1]))

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

    def test_blogpost_list(self):
        response = self.client.get(reverse('blogpost-list'))
        data = response.content
        print data
        print data[0]
        post = data['results'][0]
        self.assertEqual(post['title'], 'Post')
        self.assertContains(post['keywords_string'], "brown")
        self.assertEqual(len(post['categories']), 1)

    def test_blog_tags(self):
        data = self.client.get(reverse('blogpost-posts-by-tags')).content

    def test_blog_months(self):
        data = self.client.get(reverse('blogpost-posts-by-months')).content
        self.assertGreater(len(data), 0,
                           'Should be at least one date from post')

        now = datetime.now()
        print 'test_blog_months', data, data[0][0]
        iso_datetime, count = tuple(data[0])
        iso_datetime = self.parse_iso_datetime(iso_datetime)

        self.assertEqual(iso_datetime.month, now.month)
        self.assertEqual(count, 1)

    def test_blog_authors(self):
        data = self.client.get(reverse('blogpost-posts-by-authors')).content
        print 'test_blog_authors', data

    def test_blog_categories(self):
        data = self.client.get(reverse('blogpost-posts-by-categories')).content
        print 'test_blog_categories', data
