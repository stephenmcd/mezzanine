from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from mezzanine.core.models import Slugged, RichText

class BaseBlock(Slugged):
    login_required = models.BooleanField(_("Login required"), help_text=_("If checked, only logged in users can view this page"), default=False)
    show_title     = models.BooleanField(_("Show title"), help_text=_("If checked, only logged in users can view this page"), default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        verbose_name = _('Block')
        verbose_name_plural = _('Blocks')

class Block(BaseBlock):
    content = models.TextField(verbose_name=_('Content'), blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Block, self).save(*args, **kwargs)
        cache.delete('%s%s' % ('block_', self.slug, ))

class RichTextBlock(BaseBlock, RichText):
    def save(self, *args, **kwargs):
        super(RichTextBlock, self).save(*args, **kwargs)
        cache.delete('%s%s' % ('block_', self.slug, ))

