
from django.core.urlresolvers import resolve, reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import Displayable


class Page(Displayable):
    """
    A page in the page tree.
    """

    parent = models.ForeignKey("self", blank=True, null=True, 
        related_name="children")
    titles = models.CharField(editable=False, max_length=1000, blank=True, 
        null=True)
    ordering = models.IntegerField(editable=False, null=True)

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ("titles",)

    def __unicode__(self):
        return self.titles
        
    def get_absolute_url(self):
        return reverse("page", kwargs={"slug": self.get_slug()})

    def save(self, *args, **kwargs):
        """
        Create the titles field using the titles up the parent chain and set 
        the initial value for ordering.
        """
        if self.id is None:
            titles = [self.title]
            parent = self.parent
            while parent is not None:
                titles.insert(0, parent.title)
                parent = parent.parent
            self.titles = " / ".join(titles)
            self.ordering = Page.objects.filter(parent=self.parent).count()
        super(Page, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Update the ordering values for the sibling pages.
        """
        Page.objects.filter(parent=self.parent, ordering__gte=self.ordering
            ).update(ordering=models.F("ordering") - 1)
        super(Page, self).delete(*args, **kwargs)

    def get_slug(self):
        """
        Recursively build the slug from the chain of parents.
        """
        slug = slugify(self.title)
        if self.parent is not None:
            return "%s/%s" % (self.parent.get_slug(), slug)
        return slug
        
    def overridden(self):
        """
        Return True if the page's slug has an explicitly defined url pattern 
        and is therefore considered to be overriden.
        """
        from mezzanine.pages.views import page
        resolved_view = resolve(self.get_absolute_url())[0]
        return resolved_view != page

