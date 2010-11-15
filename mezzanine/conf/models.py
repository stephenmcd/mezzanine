
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Setting(models.Model):
    """
    Stores values for ``mezzanine.conf`` that can be edited via the admin.
    """

    name = models.CharField(max_length=50)
    value = models.CharField(max_length=2000)

    class Meta:
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")
