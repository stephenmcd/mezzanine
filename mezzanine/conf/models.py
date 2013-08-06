
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import SiteRelated


class Setting(SiteRelated):
    """
    Stores values for ``mezzanine.conf`` that can be edited via the admin.
    """

    name = models.CharField(max_length=50)
    value = models.CharField(max_length=2000)
    _order = models.IntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")

    def __unicode__(self):
        return "%s: %s" % (self.name, self.value)
