from datetime import datetime

from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.base import ModelBase
from django.template.defaultfilters import truncatewords_html
from django.utils.html import strip_tags
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.sites.managers import CurrentSiteManager

from mezzanine.core.fields import RichTextField
from mezzanine.core.managers import DisplayableManager
from mezzanine.generic.fields import KeywordsField
from mezzanine.utils.html import TagCloser
from mezzanine.utils.models import base_concrete_model
from mezzanine.utils.urls import slugify


class Slugged(models.Model):
    """
    Abstract model that handles auto-generating slugs. Each slugged
    object is also affiliated with a specific site object.
    """

    title = models.CharField(_("Title"), max_length=500)
    slug = models.CharField(_("URL"), max_length=2000, blank=True, null=True)
    site = models.ForeignKey(Site, editable=False)

    objects = CurrentSiteManager()

    class Meta:
        abstract = True
        ordering = ("title",)

    def __unicode__(self):
        return self.title

    def save(self, update_site=False, *args, **kwargs):
        """
        Create a unique slug by appending an index. Set the site to
        the current site when the record is first created, unless the
        ``update_site`` argument is explicitly set to ``True``.
        """
        if not self.slug:
            # For custom content types, use the ``Page`` instance for
            # slug lookup.
            concrete_model = base_concrete_model(Slugged, self)
            self.slug = self.get_slug()
            i = 0
            while True:
                if i > 0:
                    if i > 1:
                        self.slug = self.slug.rsplit("-", 1)[0]
                    self.slug = "%s-%s" % (self.slug, i)
                qs = concrete_model.objects.all()
                if self.id is not None:
                    qs = qs.exclude(id=self.id)
                try:
                    qs.get(slug=self.slug)
                except ObjectDoesNotExist:
                    break
                i += 1
        if update_site or not self.id:
            self.site = Site.objects.get_current()
        super(Slugged, self).save(*args, **kwargs)

    def get_slug(self):
        """
        Allows subclasses to implement their own slug creation logic.
        """
        return slugify(self)

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(),
                                        ugettext("View on site"))
    admin_link.allow_tags = True
    admin_link.short_description = ""


class MetaData(models.Model):
    """
    Abstract model that provides meta data for content.
    """

    description = models.TextField(_("Description"), blank=True)
    gen_description = models.BooleanField(_("Generate description"),
        help_text=_("If checked, the description will be automatically "
                    "generated from content. Uncheck if you want to manually "
                    "set a custom description."), default=True)
    keywords = KeywordsField(verbose_name=_("Keywords"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Set the description field on save.
        """
        if self.gen_description:
            self.description = strip_tags(self.description_from_content())
        super(MetaData, self).save(*args, **kwargs)

    def description_from_content(self):
        """
        Returns the first block or sentence of the first content-like
        field.
        """
        description = ""
        # Use the first RichTextField, or TextField if none found.
        for field_type in (RichTextField, models.TextField):
            if not description:
                for field in self._meta.fields:
                    if isinstance(field, field_type) and \
                        field.name != "description":
                        description = getattr(self, field.name)
                        if description:
                            break
        # Fall back to the title if description couldn't be determined.
        if not description:
            description = unicode(self)
        # Strip everything after the first block or sentence.
        ends = ("</p>", "<br />", "<br/>", "<br>", "</ul>",
                "\n", ". ", "! ", "? ")
        for end in ends:
            pos = description.lower().find(end)
            if pos > -1:
                description = TagCloser(description[:pos]).html
                break
        else:
            description = truncatewords_html(description, 100)
        return description


CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, _("Draft")),
    (CONTENT_STATUS_PUBLISHED, _("Published")),
)


class Displayable(Slugged, MetaData):
    """
    Abstract model that provides features of a visible page on the
    website such as publishing fields. Basis of Mezzanine pages,
    blog posts, and Cartridge products.
    """

    status = models.IntegerField(_("Status"),
        choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED)
    publish_date = models.DateTimeField(_("Published from"),
        help_text=_("With published checked, won't be shown until this time"),
        blank=True, null=True)
    expiry_date = models.DateTimeField(_("Expires on"),
        help_text=_("With published checked, won't be shown after this time"),
        blank=True, null=True)
    short_url = models.URLField(blank=True, null=True)

    objects = DisplayableManager()
    search_fields = {"keywords": 10, "title": 5}

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Set default for ``publish_date``. We can't use ``auto_add`` on
        the field as it will be blank when a blog post is created from
        the quick blog form in the admin dashboard.
        """
        if self.publish_date is None:
            self.publish_date = datetime.now()
        super(Displayable, self).save(*args, **kwargs)


class RichText(models.Model):
    """
    Provides a Rich Text field for managing general content and making
    it searchable.
    """

    content = RichTextField(_("Content"))

    search_fields = ("content",)

    class Meta:
        abstract = True


class OrderableBase(ModelBase):
    """
    Checks for ``order_with_respect_to`` on the model's inner ``Meta``
    class and if found, copies it to a custom attribute and deletes it
    since it will cause errors when used with ``ForeignKey("self")``.
    Also creates the ``ordering`` attribute on the ``Meta`` class if
    not yet provided.
    """

    def __new__(cls, name, bases, attrs):
        if "Meta" not in attrs:
            class Meta:
                pass
            attrs["Meta"] = Meta
        if hasattr(attrs["Meta"], "order_with_respect_to"):
            order_field = attrs["Meta"].order_with_respect_to
            attrs["order_with_respect_to"] = order_field
            del attrs["Meta"].order_with_respect_to
        if not hasattr(attrs["Meta"], "ordering"):
            setattr(attrs["Meta"], "ordering", ("_order",))
        return super(OrderableBase, cls).__new__(cls, name, bases, attrs)


class Orderable(models.Model):
    """
    Abstract model that provides a custom ordering integer field
    similar to using Meta's ``order_with_respect_to``, since to
    date (Django 1.2) this doesn't work with ``ForeignKey("self")``,
    or with Generic Relations. We may also want this feature for
    models that aren't ordered with respect to a particular field.
    """

    __metaclass__ = OrderableBase

    _order = models.IntegerField(_("Order"), null=True)

    class Meta:
        abstract = True

    def with_respect_to(self):
        """
        Returns a dict to use as a filter for ordering operations
        containing the original ``Meta.order_with_respect_to`` value
        if provided. If the field is a Generic Relation, the dict
        returned contains names and values for looking up the
        relation's ``ct_field`` and ``fk_field`` attributes.
        """
        try:
            name = self.order_with_respect_to
            value = getattr(self, name)
        except AttributeError:
            # No ``order_with_respect_to`` specified on the model.
            return {}
        # Support for generic relations.
        field = getattr(self.__class__, name)
        if isinstance(field, GenericForeignKey):
            names = (field.ct_field, field.fk_field)
            return dict([(name, getattr(self, name)) for name in names])
        return {name: value}

    def save(self, *args, **kwargs):
        """
        Set the initial ordering value.
        """
        if self._order is None:
            lookup = self.with_respect_to()
            lookup["_order__isnull"] = False
            concrete_model = base_concrete_model(Orderable, self)
            self._order = concrete_model.objects.filter(**lookup).count()
        super(Orderable, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Update the ordering values for siblings.
        """
        lookup = self.with_respect_to()
        lookup["_order__gte"] = self._order
        concrete_model = base_concrete_model(Orderable, self)
        after = concrete_model.objects.filter(**lookup)
        after.update(_order=models.F("_order") - 1)
        super(Orderable, self).delete(*args, **kwargs)


class Ownable(models.Model):
    """
    Abstract model that provides ownership of an object for a user.
    """

    user = models.ForeignKey("auth.User", verbose_name=_("Author"),
        related_name="%(class)ss")

    class Meta:
        abstract = True

    def is_editable(self, request):
        """
        Restrict in-line editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or request.user.id == self.user_id
