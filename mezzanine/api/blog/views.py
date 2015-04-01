import operator
from datetime import datetime
from collections import Counter

from django.db.models import Count
from django.contrib.auth.models import User

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from mezzanine.api.core.serializers import UserSerializer
from mezzanine.blog.models import BlogCategory
from mezzanine.blog.models import BlogPost

from .filters import BlogPostFilter
from .serializers import BlogCategorySerializer
from .serializers import BlogPostSerializer


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogPost.objects.published()
    serializer_class = BlogPostSerializer
    filter_class = BlogPostFilter
    paginate_by = 5
    paginate_by_param = 'page'

    @list_route()
    def recent_posts(self, request):
        blog_posts = self.queryset.order_by('-publish_date')
        serialized_posts = BlogPostSerializer(list(blog_posts[:5]), many=True)
        return Response(serialized_posts.data)

    @list_route()
    def posts_by_months(self, request):

        posts_dates = self.queryset.values_list("publish_date", flat=True)

        normalized_dates = []
        for d in posts_dates:
            normalized_date = datetime(d.year, d.month, 1).isoformat()
            normalized_dates.append(normalized_date)

        counted_dates = Counter(normalized_dates)
        sorted_date = sorted(counted_dates.items(), key=operator.itemgetter(0),
                             reverse=True)
        return Response(sorted_date)

    @list_route()
    def posts_by_categories(self, request):
        posts = self.queryset
        categories = BlogCategory.objects.filter(blogposts__in=posts)
        counted_categories = categories.annotate(post_count=Count("blogposts"))
        counted_categories = list(counted_categories)

        serialized = BlogCategorySerializer(counted_categories, many=True)
        return Response(serialized.data)

    @list_route()
    def posts_by_authors(self, request):
        blog_posts = BlogPost.objects.published()
        authors = User.objects.filter(blogposts__in=blog_posts)
        posts_per_author = list(authors.annotate(post_count=Count("blogposts")))
        serialized = UserSerializer(posts_per_author, many=True)
        return Response(serialized.data)


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
