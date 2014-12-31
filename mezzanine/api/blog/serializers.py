from rest_framework import serializers

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.api.core.serializers import UserSerializer
from mezzanine.api.generic.serializers import ThreadedCommentSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'slug']


class BlogPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user')
    categories = BlogCategorySerializer(source='categories', many=True)
    comments = ThreadedCommentSerializer(source='comments', many=True)

    class Meta:
        model = BlogPost
        fields = ['id','slug', 'user', 'categories', 'content', 'title',
                  'allow_comments', 'comments_count', 'comments',
                  'publish_date', 'keywords_string', 'featured_image']
