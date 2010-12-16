
from django.core.urlresolvers import resolve, reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import Displayable, Orderable, Content
from mezzanine.utils.urls import admin_url


class Page(Orderable, Displayable):
    """
    A page in the page tree. This is the base class that custom content types 
    need to subclass.
    """

    parent = models.ForeignKey("Page", blank=True, null=True,
        related_name="children")
    in_navigation = models.BooleanField(_("Show in navigation"), default=True)
    in_footer = models.BooleanField(_("Show in footer"))
    titles = models.CharField(editable=False, max_length=1000, null=True)
    content_model = models.CharField(editable=False, max_length=50, null=True)
    login_required = models.BooleanField(_("Login required"),
        help_text=_("If checked, only logged in users can view this page"))

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ("titles",)
        order_with_respect_to = "parent"

    def __unicode__(self):
        return self.titles

    @models.permalink
    def get_absolute_url(self):
        return ("page", (), {"slug": self.get_slug()})

    def get_admin_url(self):
        return admin_url(self, "change", self.id)

    def save(self, *args, **kwargs):
        """
        Create the titles field using the titles up the parent chain and set
        the initial value for ordering.
        """
        if self.id is None:
            self.content_model = self._meta.object_name.lower()
        titles = [self.title]
        parent = self.parent
        while parent is not None:
            titles.insert(0, parent.title)
            parent = parent.parent
        self.titles = " / ".join(titles)
        super(Page, self).save(*args, **kwargs)

    def get_content_model(self):
        """
        Provies a generic method of retrieving the instance of the custom 
        content type's model for this page.
        """
        return getattr(self, self.content_model, None)

    def get_slug(self):
        """
        Recursively build the slug from the chain of parents.
        """
        slug = slugify(self.title)
        if self.parent is not None:
            return "%s/%s" % (self.parent.get_slug(), slug)
        return slug

    def reset_slugs(self):
        """
        Called when the parent page is changed in the admin and the slug 
        plus all child slugs need to be recreated given the new parent.
        """
        if not self.overridden():
            self.slug = None
            self.save()
        for child in self.children.all():
            child.reset_slugs()

    def overridden(self):
        """
        Return ``True`` if the page's slug has an explicitly defined
        urlpattern and is therefore considered to be overridden.
        """
        from mezzanine.pages.views import page
        page_url = reverse("page", kwargs={"slug": self.slug})
        resolved_view = resolve(page_url)[0]
        return resolved_view != page

    def set_menu_helpers(self, slug):
        """
        Called from the ``page_menu`` template tag and assigns a handful 
        of properties based on the current URL that are used within the 
        various types of menus.
        """
        slug = slug.strip("/")
        parent_slug = lambda slug: "/".join(slug.split("/")[:-1]) + "/"
        self.is_current_sibling = parent_slug(slug) == parent_slug(self.slug)
        self.is_current_or_ascendant = (slug + "/").startswith(self.slug + "/")
        self.is_current = slug == self.slug
        self.is_primary = self.parent_id is None
        self.is_child = (slug + "/") == parent_slug(self.slug)
        self.html_id = self.slug.replace("/", "-")
        self.branch_level = 0


class ContentPage(Page, Content):
    """
    Implements the default type of page with a single HTML content field.
    """

    class Meta:
        verbose_name = _("Content page")
        verbose_name_plural = _("Content pages")
