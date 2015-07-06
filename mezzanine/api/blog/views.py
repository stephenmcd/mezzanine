import operator
from datetime import datetime
from collections import Counter

from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from mezzanine.blog.models import BlogCategory
from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import AssignedKeyword
from mezzanine.generic.models import Keyword

from .filters import BlogPostFilter
from .serializers import BlogCategorySerializer
from .serializers import BlogPostSerializer


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    """Blog endpoint."""

    queryset = BlogPost.objects.published()
    serializer_class = BlogPostSerializer
    filter_class = BlogPostFilter
    paginate_by = 5
    paginate_by_param = 'page'

    def get_queryset(self):
        return BlogPost.objects.published()

    @list_route(methods=['get'], url_path='recent-posts')
    def recent_posts(self, request):
        """Return last five posts from blog."""
        blog_posts = self.queryset.order_by('-publish_date')
        serialized_posts = BlogPostSerializer(list(blog_posts[:5]), many=True)
        return Response(serialized_posts.data)

    @list_route(methods=['get'], url_path='posts-by-months')
    def blog_months(self, request):
        """
        Return as JSON list of months with number of posts per that month.

        Used mostly for list a months with number of posts. For ex.
            Archive 2015
                July (1)
                June (2)
                January (1)
            Archive 2014
                December (2)
        List is sorted by field publish_date in descending order.

        :return: list that item of the list consist of
                 date in iso format and counted posts.
            `[
                "2015-07-01T00:00:00" : 1,
                "2015-06-01T00:00:00" : 2,
                "2015-01-01T00:00:00" : 1,
                "2014-12-01T00:00:00" : 2,
                ...
            ]`
        """
        post_dates = self.get_queryset().values_list("publish_date", flat=True)

        normalized_dates = []
        for d in post_dates:
            normalized_date = datetime(d.year, d.month, 1).isoformat()
            normalized_dates.append(normalized_date)

        counted_dates = Counter(normalized_dates)
        sorted_date = sorted(counted_dates.items(), key=operator.itemgetter(0),
                             reverse=True)
        return Response(sorted_date)

    @list_route(methods=['get'], url_path='posts-by-categories')
    def blog_categories(self, request):
        """
        Return as JSON selected categories with number of blog posts.
        """
        posts = self.get_queryset()
        categories = BlogCategory.objects.filter(blogposts__in=posts)
        categories = categories.annotate(post_count=Count("blogposts"))

        data = [
            {'slug': cat.slug, 'title': cat.title, 'count': cat.post_count}
            for cat in list(categories)
        ]
        return Response(data)

    @list_route(methods=['get'], url_path='posts-by-authors')
    def blog_authors(self, request):
        """
        Return as JSON list of authors with number their blog posts.

        :return: list, where items are dictionary with keys `author`
                 and `count` for ex.
                 [
                    { 'author': 'Chairman', count: 1 },
                    { 'author': 'Stephen McDonald', count: 5 }
                 ]
        """
        blog_posts = self.get_queryset()
        authors = User.objects.filter(blogposts__in=blog_posts)
        authors = list(authors.annotate(post_count=Count("blogposts")))

        data = [{'author': author.get_full_name() or author.username,
                 'count': author.post_count}
                for author in authors]
        return Response(data)

    @list_route(methods=['get'], url_path='posts-by-tags')
    def blog_tags(self, request):
        """
        Return as JSON list of tags with number of their use in blog posts.
        """
        content_type = ContentType.objects.get(app_label='blog',
                                               model='blogpost')
        assigned = AssignedKeyword.objects.filter(content_type=content_type)
        keywords = Keyword.objects.filter(assignments__in=assigned)
        keywords = keywords.annotate(item_count=Count("assignments"))

        data = [{'title': kywd.title, 'slug': kywd.slug,
                 'count': kywd.item_count}
                for kywd in keywords]
        return Response(data)


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Blog Category endpoint."""

    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
