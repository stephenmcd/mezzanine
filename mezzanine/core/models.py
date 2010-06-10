
from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify, truncatewords_html
from django.utils.translation import ugettext, ugettext_lazy as _

from mezzanine.core.managers import PublishedManager
from mezzanine import settings as blog_settings


class Displayable(models.Model):
    """
    Abstract model representing a visible object on the website with common 
    functionality such as auto slug creation and an active field for toggling 
    visibility.
    """

    title = models.CharField(_("Title"), max_length=100)
    content = models.TextField(_("Content"))
    description = models.TextField(_("Description"), blank=True)
    status = models.IntegerField(_("Status"), 
        choices=blog_settings.CONTENT_STATUS_CHOICES, 
        default=blog_settings.CONTENT_STATUS_DRAFT)
    publish_date = models.DateTimeField(_("Published from"), blank=True, 
        default=datetime.now)
    slug = models.SlugField(max_length=100, editable=False, null=True)
    keywords = models.ManyToManyField("Keyword", verbose_name=_("Keywords"),
        blank=True)
    short_url = models.URLField(blank=True, null=True)
        
    objects = PublishedManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        """
        Create the description from the content if none given, and create a 
        unique slug from the title by appending an index.
        """
        if self.publish_date is None:
            # publish_date will be blank when a blog post is created from the 
            # quick blog form in the admin dashboard.
            self.publish_date = datetime.now()
        if not self.description:
            for s in ("</p>", "\n", ". "):
                if s in self.content:
                    self.description = self.content.split(s)[0] + s
                    break
            else:
                self.description = truncatewords_html(self.content, 100)
        if self.id is None:
            self.slug = self.get_slug()
            i = 0
            while True:
                if i > 0:
                    self.slug = "%s-%s" % (self.slug, i)
                if not self.__class__.objects.filter(slug=self.slug):
                    break
                i += 1
        super(Displayable, self).save(*args, **kwargs)
        
    def get_slug(self):
        return slugify(self.title)
    
    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), 
            ugettext("View on site"))
    admin_link.allow_tags = True
    admin_link.short_description = ""
                
class Keyword(models.Model):
    """
    Keywords/tags which are managed via a custom Javascript based widget in the 
    admin.
    """

    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"
        ordering = ("value",)

    value = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.value
    
