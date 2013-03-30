
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site
from django.db.models import get_models

from mezzanine.conf import settings
from mezzanine.core.models import Displayable
from mezzanine.utils.sites import current_site_id
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
                for item in (model.objects.published().filter(in_sitemap=True)
                             .exclude(slug__startswith="http://")
                             .exclude(slug__startswith="https://")):
                    items[item.get_absolute_url()] = item
        return items.values()

    def lastmod(self, obj):
        if blog_installed and isinstance(obj, BlogPost):
            return obj.publish_date

    def get_urls(self, **kwargs):
        """
        Ensure the correct host by injecting the current site.
        """
        kwargs["site"] = Site.objects.get(id=current_site_id())
        return super(DisplayableSitemap, self).get_urls(**kwargs)
