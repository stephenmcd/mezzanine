from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site

from mezzanine.conf import settings
from mezzanine.core.models import Displayable
from mezzanine.utils.sites import current_site_id

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
        return list(Displayable.objects.url_map(in_sitemap=True).values())

    def lastmod(self, obj):
        if blog_installed and isinstance(obj, BlogPost):
            return obj.updated or obj.publish_date

    def get_urls(self, **kwargs):
        """
        Ensure the correct host by injecting the current site.
        """
        kwargs["site"] = Site.objects.get(id=current_site_id())
        return super().get_urls(**kwargs)
