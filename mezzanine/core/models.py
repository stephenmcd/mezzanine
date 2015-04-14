from __future__ import unicode_literals
from future.builtins import str
from future.utils import with_metaclass

from json import loads
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlopen, urlencode

from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.template.defaultfilters import truncatewords_html
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.timesince import timesince
from django.utils.timezone import now
from django.utils.translation import ugettext, ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import RichTextField, OrderField
from mezzanine.core.managers import DisplayableManager, CurrentSiteManager
from mezzanine.generic.fields import KeywordsField
from mezzanine.utils.html import TagCloser
from mezzanine.utils.models import base_concrete_model, get_user_model_name
from mezzanine.utils.sites import current_site_id, current_request
from mezzanine.utils.urls import admin_url, slugify, unique_slug


user_model_name = get_user_model_name()


class SiteRelated(models.Model):
    """
    Abstract model for all things site-related. Adds a foreignkey to
    Django's ``Site`` model, and filters by site with all querysets.
    See ``mezzanine.utils.sites.current_site_id`` for implementation
    details.
    """

    objects = CurrentSiteManager()

    class Meta:
        abstract = True

    site = models.ForeignKey("sites.Site", editable=False)

    def save(self, update_site=False, *args, **kwargs):
        """
        Set the site to the current site when the record is first
        created, or the ``update_site`` argument is explicitly set
        to ``True``.
        """
        if update_site or (self.id is None and self.site_id is None):
            self.site_id = current_site_id()
        super(SiteRelated, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Slugged(SiteRelated):
    """
    Abstract model that handles auto-generating slugs. Each slugged
    object is also affiliated with a specific site object.
    """

    title = models.CharField(_("Title"), max_length=500)
    slug = models.CharField(_("URL"), max_length=2000, blank=True, null=True,
            help_text=_("Leave blank to have the URL auto-generated from "
                        "the title."))

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        If no slug is provided, generates one before saving.
        """
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super(Slugged, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Create a unique slug by passing the result of get_slug() to
        utils.urls.unique_slug, which appends an index if necessary.
        """
        # For custom content types, use the ``Page`` instance for
        # slug lookup.
        concrete_model = base_concrete_model(Slugged, self)
        slug_qs = concrete_model.objects.exclude(id=self.id)
        return unique_slug(slug_qs, "slug", self.get_slug())

    def get_slug(self):
        """
        Allows subclasses to implement their own slug creation logic.
        """
        attr = "title"
        if settings.USE_MODELTRANSLATION:
            from modeltranslation.utils import build_localized_fieldname
            attr = build_localized_fieldname(attr, settings.LANGUAGE_CODE)
        # Get self.title_xx where xx is the default language, if any.
        # Get self.title otherwise.
        return slugify(getattr(self, attr, None) or self.title)

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(),
                                        ugettext("View on site"))
    admin_link.allow_tags = True
    admin_link.short_description = ""


class MetaData(models.Model):
    """
    Abstract model that provides meta data for content.
    """

    _meta_title = models.CharField(_("Title"), null=True, blank=True,
        max_length=500,
        help_text=_("Optional title to be used in the HTML title tag. "
                    "If left blank, the main title field will be used."))
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

    def meta_title(self):
        """
        Accessor for the optional ``_meta_title`` field, which returns
        the string version of the instance if not provided.
        """
        return self._meta_title or str(self)

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
                    if (isinstance(field, field_type) and
                            field.name != "description"):
                        description = getattr(self, field.name)
                        if description:
                            from mezzanine.core.templatetags.mezzanine_tags \
                                                    import richtext_filters
                            description = richtext_filters(description)
                            break
        # Fall back to the title if description couldn't be determined.
        if not description:
            description = str(self)
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


class TimeStamped(models.Model):
    """
    Provides created and updated timestamps on models.
    """

    class Meta:
        abstract = True

    created = models.DateTimeField(null=True, editable=False)
    updated = models.DateTimeField(null=True, editable=False)

    def save(self, *args, **kwargs):
        _now = now()
        self.updated = _now
        if not self.id:
            self.created = _now
        super(TimeStamped, self).save(*args, **kwargs)


CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, _("Draft")),
    (CONTENT_STATUS_PUBLISHED, _("Published")),
)

SHORT_URL_UNSET = "unset"


class Displayable(Slugged, MetaData, TimeStamped):
    """
    Abstract model that provides features of a visible page on the
    website such as publishing fields. Basis of Mezzanine pages,
    blog posts, and Cartridge products.
    """

    status = models.IntegerField(_("Status"),
        choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED,
        help_text=_("With Draft chosen, will only be shown for admin users "
            "on the site."))
    publish_date = models.DateTimeField(_("Published from"),
        help_text=_("With Published chosen, won't be shown until this time"),
        blank=True, null=True)
    expiry_date = models.DateTimeField(_("Expires on"),
        help_text=_("With Published chosen, won't be shown after this time"),
        blank=True, null=True)
    short_url = models.URLField(blank=True, null=True)
    in_sitemap = models.BooleanField(_("Show in sitemap"), default=True)

    objects = DisplayableManager()
    search_fields = {"keywords": 10, "title": 5}

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Set default for ``publish_date``. We can't use ``auto_now_add`` on
        the field as it will be blank when a blog post is created from
        the quick blog form in the admin dashboard.
        """
        if self.publish_date is None:
            self.publish_date = now()
        super(Displayable, self).save(*args, **kwargs)

    def get_admin_url(self):
        return admin_url(self, "change", self.id)

    def publish_date_since(self):
        """
        Returns the time since ``publish_date``.
        """
        return timesince(self.publish_date)
    publish_date_since.short_description = _("Published from")

    def get_absolute_url(self):
        """
        Raise an error if called on a subclass without
        ``get_absolute_url`` defined, to ensure all search results
        contains a URL.
        """
        name = self.__class__.__name__
        raise NotImplementedError("The model %s does not have "
                                  "get_absolute_url defined" % name)

    def get_absolute_url_with_host(self):
        """
        Returns host + ``get_absolute_url`` - used by the various
        ``short_url`` mechanics below.

        Technically we should use ``self.site.domain``, here, however
        if we were to invoke the ``short_url`` mechanics on a list of
        data (eg blog post list view), we'd trigger a db query per
        item. Using ``current_request`` should provide the same
        result, since site related data should only be loaded based
        on the current host anyway.
        """
        return current_request().build_absolute_uri(self.get_absolute_url())

    def set_short_url(self):
        """
        Generates the ``short_url`` attribute if the model does not
        already have one. Used by the ``set_short_url_for`` template
        tag and ``TweetableAdmin``.

        If no sharing service is defined (bitly is the one implemented,
        but others could be by overriding ``generate_short_url``), the
        ``SHORT_URL_UNSET`` marker gets stored in the DB. In this case,
        ``short_url`` is temporarily (eg not persisted) set to
        host + ``get_absolute_url`` - this is so that we don't
        permanently store ``get_absolute_url``, since it may change
        over time.
        """
        if self.short_url == SHORT_URL_UNSET:
            self.short_url = self.get_absolute_url_with_host()
        elif not self.short_url:
            self.short_url = self.generate_short_url()
            self.save()

    def generate_short_url(self):
        """
        Returns a new short URL generated using bit.ly if credentials for the
        service have been specified.
        """
        from mezzanine.conf import settings
        settings.use_editable()
        if settings.BITLY_ACCESS_TOKEN:
            url = "https://api-ssl.bit.ly/v3/shorten?%s" % urlencode({
                "access_token": settings.BITLY_ACCESS_TOKEN,
                "uri": self.get_absolute_url_with_host(),
            })
            response = loads(urlopen(url).read().decode("utf-8"))
            if response["status_code"] == 200:
                return response["data"]["url"]
        return SHORT_URL_UNSET

    def _get_next_or_previous_by_publish_date(self, is_next, **kwargs):
        """
        Retrieves next or previous object by publish date. We implement
        our own version instead of Django's so we can hook into the
        published manager and concrete subclasses.
        """
        arg = "publish_date__gt" if is_next else "publish_date__lt"
        order = "publish_date" if is_next else "-publish_date"
        lookup = {arg: self.publish_date}
        concrete_model = base_concrete_model(Displayable, self)
        try:
            queryset = concrete_model.objects.published
        except AttributeError:
            queryset = concrete_model.objects.all
        try:
            return queryset(**kwargs).filter(**lookup).order_by(order)[0]
        except IndexError:
            pass

    def get_next_by_publish_date(self, **kwargs):
        """
        Retrieves next object by publish date.
        """
        return self._get_next_or_previous_by_publish_date(True, **kwargs)

    def get_previous_by_publish_date(self, **kwargs):
        """
        Retrieves previous object by publish date.
        """
        return self._get_next_or_previous_by_publish_date(False, **kwargs)


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


class Orderable(with_metaclass(OrderableBase, models.Model)):
    """
    Abstract model that provides a custom ordering integer field
    similar to using Meta's ``order_with_respect_to``, since to
    date (Django 1.2) this doesn't work with ``ForeignKey("self")``,
    or with Generic Relations. We may also want this feature for
    models that aren't ordered with respect to a particular field.
    """

    _order = OrderField(_("Order"), null=True)

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
            return dict([(n, getattr(self, n)) for n in names])
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

    def _get_next_or_previous_by_order(self, is_next, **kwargs):
        """
        Retrieves next or previous object by order. We implement our
        own version instead of Django's so we can hook into the
        published manager, concrete subclasses and our custom
        ``with_respect_to`` method.
        """
        lookup = self.with_respect_to()
        lookup["_order"] = self._order + (1 if is_next else -1)
        concrete_model = base_concrete_model(Orderable, self)
        try:
            queryset = concrete_model.objects.published
        except AttributeError:
            queryset = concrete_model.objects.filter
        try:
            return queryset(**kwargs).get(**lookup)
        except concrete_model.DoesNotExist:
            pass

    def get_next_by_order(self, **kwargs):
        """
        Retrieves next object by order.
        """
        return self._get_next_or_previous_by_order(True, **kwargs)

    def get_previous_by_order(self, **kwargs):
        """
        Retrieves previous object by order.
        """
        return self._get_next_or_previous_by_order(False, **kwargs)


class Ownable(models.Model):
    """
    Abstract model that provides ownership of an object for a user.
    """

    user = models.ForeignKey(user_model_name, verbose_name=_("Author"),
        related_name="%(class)ss")

    class Meta:
        abstract = True

    def is_editable(self, request):
        """
        Restrict in-line editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or request.user.id == self.user_id


class SitePermission(models.Model):
    """
    Permission relationship between a user and a site that's
    used instead of ``User.is_staff``, for admin and inline-editing
    access.
    """

    user = models.OneToOneField(user_model_name, verbose_name=_("Author"),
        related_name="%(class)ss")
    sites = models.ManyToManyField("sites.Site", blank=True,
                                   verbose_name=_("Sites"))

    class Meta:
        verbose_name = _("Site permission")
        verbose_name_plural = _("Site permissions")


def create_site_permission(sender, **kw):
    sender_name = "%s.%s" % (sender._meta.app_label, sender._meta.object_name)
    if sender_name.lower() != user_model_name.lower():
        return
    user = kw["instance"]
    if user.is_staff and not user.is_superuser:
        perm, created = SitePermission.objects.get_or_create(user=user)
        if created or perm.sites.count() < 1:
            perm.sites.add(current_site_id())

# We don't specify the user model here, because with Django's custom
# user models, everything explodes. So we check the name of it in
# the signal.
post_save.connect(create_site_permission)
