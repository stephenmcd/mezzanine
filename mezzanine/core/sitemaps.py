
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
        item_urls = set()
        for model in get_models():
            if issubclass(model, Displayable):
                for item in model.objects.published():
                    url = item.get_absolute_url()
                    # check if the url of that item was already seen
                    # (this might happen for Page items and subclasses of Page like RichTextPage)
                    if not url in item_urls:
                        items.append(item)
                        item_urls.add(url)
        return items
