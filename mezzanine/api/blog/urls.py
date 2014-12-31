from django.conf.urls import patterns, url
import views

urlpatterns = patterns("mezzanine.api.blog.views",
    url('^blog_post$', views.BlogPostsAPIView.as_view()),
    url('^blog_category$', views.BlogCategoryAPIView.as_view()),

    url('^recent_posts$', views.blog_recent_posts),
    url('^recent_posts/(?P<number>\d+)$', views.blog_recent_posts),

    url('^posts_by_categories$', views.posts_by_categories),
    url('^posts_by_months$', views.posts_by_months),
    url('^posts_by_authors$', views.posts_by_authors),
)
