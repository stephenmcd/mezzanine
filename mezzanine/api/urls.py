from rest_framework.routers import DefaultRouter

from blog.views import BlogViewSet, BlogCategoryViewSet
from pages.views import PagesViewSet

router = DefaultRouter()
router.register(r'blog', BlogViewSet)
router.register(r'categories', BlogCategoryViewSet)

router.register(r'pages', PagesViewSet)

urlpatterns = router.urls
