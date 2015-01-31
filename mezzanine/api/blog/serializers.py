from rest_framework import serializers

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.api.core.serializers import UserSerializer
from mezzanine.api.generic.serializers import ThreadedCommentSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'slug']


class BlogPostSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    categories = BlogCategorySerializer(many=True)
    comments = ThreadedCommentSerializer(many=True)

    class Meta:
        model = BlogPost
        fields = ['id','slug', 'user', 'categories', 'content', 'title',
                  'allow_comments', 'comments_count', 'comments',
                  'publish_date', 'keywords_string', 'featured_image']
