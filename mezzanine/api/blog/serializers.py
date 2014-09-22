from rest_framework import serializers

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.api.core.serializers import UserSerializer

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user')
    categories = BlogCategorySerializer(source='categories', many=True, required=False, read_only=True)
    class Meta:
        model = BlogPost
        fields = ['id','slug', 'user', 'categories', 'content', 'title', 'allow_comments', 'comments_count', 'publish_date', 'keywords_string', 'featured_image']

