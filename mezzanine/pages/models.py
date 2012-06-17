from django.core.urlresolvers import resolve, reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import Displayable, Orderable, RichText
from mezzanine.utils.urls import admin_url, slugify


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

    def get_absolute_url(self):
        """
        URL for a page - for ``Link`` page types, simply return its
        slug since these don't have an actual URL pattern. Also handle
        the special case of the homepage being a page object.
        """
        slug = self.slug
        if self.content_model == "link":
            # Ensure the URL is absolute.
            if not slug.lower().startswith("http"):
                slug = "/" + self.slug.lstrip("/")
            return slug
        if slug == "/":
            return reverse("home")
        else:
            return reverse("page", kwargs={"slug": slug})

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

    @classmethod
    def get_content_models(cls):
        """
        Return all Page subclasses.
        """
        is_content_model = lambda m: m is not Page and issubclass(m, Page)
        return filter(is_content_model, models.get_models())

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
            return "%s/%s" % (self.parent.slug, slug)
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
        Returns ``True`` if the page's slug has an explicitly defined
        urlpattern and is therefore considered to be overridden.
        """
        from mezzanine.pages.views import page
        page_url = reverse("page", kwargs={"slug": self.slug})
        resolved_view = resolve(page_url)[0]
        return resolved_view != page

    def can_add(self, request):
        """
        Dynamic ``add`` permission for content types to override.
        """
        return True

    def can_change(self, request):
        """
        Dynamic ``change`` permission for content types to override.
        """
        return True

    def can_delete(self, request):
        """
        Dynamic ``delete`` permission for content types to override.
        """
        return True

    def set_helpers(self, context):
        """
        Called from the ``page_menu`` template tag and assigns a
        handful of properties based on the current page, that are used
        within the various types of menus.
        """
        current_page = context["_current_page"]
        current_page_id = getattr(current_page, "id", None)
        current_parent_id = getattr(current_page, "parent_id", None)
        # Am I a child of the current page?
        self.is_child = self.parent_id == current_page_id
        # Is my parent the same as the current page's?
        self.is_current_sibling = self.parent_id == current_parent_id
        # Am I the current page?
        from mezzanine.urls import PAGES_SLUG
        try:
            request = context["request"]
        except KeyError:
            # No request context, most likely when tests are run.
            self.is_current = False
        else:
            slug = request.path.strip("/").replace(PAGES_SLUG, "", 1)
            self.is_current = self.slug == slug

        # Is the current page me or any page up the parent chain?
        def is_c_or_a(page_id):
            parent_id = context["_parent_page_ids"].get(page_id)
            return self.id == page_id or (parent_id and is_c_or_a(parent_id))
        self.is_current_or_ascendant = lambda: bool(is_c_or_a(current_page_id))
        # Am I a primary page?
        self.is_primary = self.parent_id is None
        # What's an ID I can use in HTML?
        self.html_id = self.slug.replace("/", "-")
        # Default branch level - gets assigned in the page_menu tag.
        self.branch_level = 0


class RichTextPage(Page, RichText):
    """
    Implements the default type of page with a single Rich Text
    content field.
    """

    class Meta:
        verbose_name = _("Rich text page")
        verbose_name_plural = _("Rich text pages")


class Link(Page):
    """
    A general content type for creating external links in the page
    menu.
    """

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")
