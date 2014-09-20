import django_filters
from rest_framework import generics

from mezzanine.blog.models import BlogPost, BlogCategory
from .serializers import BlogCategorySerializer, BlogPostSerializer


class BlogPostFilter(django_filters.FilterSet):
    min_publish_date = django_filters.DateTimeFilter(name="publish_date", lookup_type='gte')
    max_publish_date = django_filters.DateTimeFilter(name="publish_date", lookup_type='lte')
    title = django_filters.CharFilter(name='title', lookup_type='contains')
    class Meta:
        model = BlogPost
        fields = ['title']


class BlogPostsAPIView(generics.ListAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    filter_class = BlogPostFilter
    paginate_by = 5

class BlogCategoryAPIView(generics.ListAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
