
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site


class Setting(models.Model):
    """
    Stores values for ``mezzanine.conf`` that can be edited via the admin.
    """

    name = models.CharField(max_length=50)
    value = models.CharField(max_length=2000)
    site = models.ForeignKey(Site, editable=False)

    class Meta:
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")

    def save(self, *args, **kwargs):
        """
        Set the site to the current site.
        """

        self.site = Site.objects.get_current()
        super(Setting, self).save(*args, **kwargs)
