from datetime import datetime

from django.db.models import Count
from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mezzanine.api.core.serializers import UserSerializer
from mezzanine.blog.models import BlogCategory
from mezzanine.blog.models import BlogPost

from .filters import BlogPostFilter
from .serializers import BlogCategorySerializer
from .serializers import BlogPostSerializer


class BlogPostsAPIView(generics.ListAPIView):

    """
    Returns a list of all **active** accounts in the system.
    """
    queryset = BlogPost.objects.published()
    serializer_class = BlogPostSerializer
    filter_class = BlogPostFilter
    paginate_by = 5
    paginate_by_param = 'page'


class BlogCategoryAPIView(generics.ListAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer


@api_view(['GET'])
def blog_recent_posts(request, number=5):
    blog_posts = BlogPost.objects.published().select_related("user")
    serialized_posts = BlogPostSerializer(list(blog_posts[:number]), many=True)
    return Response(serialized_posts.data)


@api_view(['GET'])
def posts_by_categories(*args):
    """
    receives number of blog posts per category
    """
    posts = BlogPost.objects.published()
    categories = BlogCategory.objects.filter(blogposts__in=posts)
    counted_categories = categories.annotate(post_count=Count("blogposts"))
    counted_categories = list(counted_categories)

    serialized = BlogCategorySerializer(counted_categories, many=True)
    return Response(serialized.data)


@api_view(['GET'])
def posts_by_months(*args):
    """
    receives number of blog posts per month
    """
    dates = BlogPost.objects.published().values_list("publish_date", flat=True)
    date_dicts = [{"date": datetime(d.year, d.month, 1)} for d in dates]
    month_dicts = []
    for date_dict in date_dicts:
        if date_dict not in month_dicts:
            month_dicts.append(date_dict)
    for i, date_dict in enumerate(month_dicts):
        month_dicts[i]["post_count"] = date_dicts.count(date_dict)
    return Response(month_dicts)


@api_view(['GET'])
def posts_by_authors(*args):
    """
    receives number of blog posts per author
    """
    blog_posts = BlogPost.objects.published()
    authors = User.objects.filter(blogposts__in=blog_posts)
    posts_per_author = list(authors.annotate(post_count=Count("blogposts")))
    serialized = UserSerializer(posts_per_author, many=True)
    return Response(serialized.data)
