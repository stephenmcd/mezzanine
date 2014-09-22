from django.conf.urls import patterns, url
from .views import BlogPostsAPIView, BlogCategoryAPIView

urlpatterns = patterns("mezzanine.api.blog.views",
    url('^blog_post$', BlogPostsAPIView.as_view(), name='blogpost_api'),
    url('^blog_category$', BlogCategoryAPIView.as_view(), name='blogcategory_api'),
)
