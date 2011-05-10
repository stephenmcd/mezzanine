
from django.contrib.sitemaps import Sitemap
from django.db.models import get_models

from mezzanine.core.models import Displayable


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
        items = []
        for model in get_models():
            if issubclass(model, Displayable):
                items.extend(model.objects.published())
        return items
