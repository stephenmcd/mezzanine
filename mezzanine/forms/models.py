
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _

from mezzanine.core.fields import HtmlField
from mezzanine.core.models import Orderable
from mezzanine.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH
from mezzanine.pages.models import Page


FIELD_CHOICES = (
    ("CharField", _("Single line text")),
    ("CharField/django.forms.Textarea", _("Multi line text")),
    ("EmailField", _("Email")),
    ("BooleanField", _("Check box")),
    ("ChoiceField", _("Drop down")),
    ("MultipleChoiceField", _("Multi select")),
    ("FileField", _("File upload")),
    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
    ("DateTimeField", _("Date/time")),
)


class Form(Page):
    """
    A user-built form.
    """

    response = HtmlField(_("Response"))
    send_email = models.BooleanField(_("Send email"), default=True,
        help_text=_("If checked, the person entering the form will be sent an "
                                                                    "email"))
    email_from = models.EmailField(_("From address"), blank=True,
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send copies to"), blank=True,
        help_text=_("One or more email addresses, separated by commas"),
        max_length=200)

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")


class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)


class Field(Orderable):
    """
    A field for a user-built form.
    """

    form = models.ForeignKey("Form", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES,
        max_length=50)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text="Comma separated options where applicable")

    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        order_with_respect_to = "form"

    def __unicode__(self):
        return self.label


class FormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    form = models.ForeignKey("Form", related_name="entries")
    entry_time = models.DateTimeField(_("Date/time"))

    class Meta:
        verbose_name = _("Form entry")
        verbose_name_plural = _("Form entries")


class FieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """

    entry = models.ForeignKey("FormEntry", related_name="fields")
    field_id = models.IntegerField()
    value = models.CharField(max_length=FIELD_MAX_LENGTH)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")
