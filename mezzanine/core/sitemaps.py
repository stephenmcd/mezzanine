
from django.contrib.sitemaps import Sitemap
from django.db.models import get_models

from mezzanine.conf import settings
from mezzanine.core.models import Displayable
from mezzanine.utils.urls import home_slug


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
        ``Displayable``, excluding those that point to external sites.
        """
        # Fake homepage object.
        home = Displayable()
        setattr(home, "get_absolute_url", home_slug)
        items = {home.get_absolute_url(): home}
        for model in get_models():
            if issubclass(model, Displayable):
                for item in (model.objects.published()
                             .exclude(slug__startswith="http://")
                             .exclude(slug__startswith="https://")):
                    items[item.get_absolute_url()] = item
        return items.values()

    def lastmod(self, obj):
        if blog_installed and isinstance(obj, BlogPost):
            return obj.publish_date
