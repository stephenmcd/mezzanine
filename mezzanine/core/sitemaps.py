
from django.contrib.sitemaps import Sitemap
from django.db.models import get_models

from mezzanine.conf import settings
from mezzanine.core.models import Displayable

blog_installed = "mezzanine.blog" in settings.INSTALLED_APPS
if blog_installed:
    from mezzanine.blog.models import BlogPost


class DisplayableSitemap(Sitemap):
    """
    Sitemap class for Django's sitemaps framework that returns
    all published items for models that subclass ``Displayable``.
    """

    def items(self):
        """
        Return all published items for models that subclass
        ``Displayable``.
        """
        items = {}
        for model in get_models():
            if issubclass(model, Displayable):
                for item in model.objects.published():
                    items[item.get_absolute_url()] = item
        return items.values()

    def lastmod(self, obj):
        if blog_installed and isinstance(obj, BlogPost):
            return obj.publish_date
