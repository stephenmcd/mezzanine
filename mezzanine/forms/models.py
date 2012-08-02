
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import RichTextField
from mezzanine.core.models import Orderable, RichText
from mezzanine.forms import fields
from mezzanine.pages.models import Page


class Form(Page, RichText):
    """
    A user-built form.
    """

    button_text = models.CharField(_("Button text"), max_length=50,
        default=_("Submit"))
    response = RichTextField(_("Response"))
    send_email = models.BooleanField(_("Send email to user"), default=True,
        help_text=_("To send an email to the email address supplied in "
                    "the form upon submission, check this box."))
    email_from = models.EmailField(_("From address"), blank=True,
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send email to others"), blank=True,
        help_text=_("Provide a comma separated list of email addresses "
                    "to be notified upon form submission. Leave blank to "
                    "disable notifications."),
        max_length=200)
    email_subject = models.CharField(_("Subject"), max_length=200, blank=True)
    email_message = models.TextField(_("Message"), blank=True,
        help_text=_("Emails sent based on the above options will contain "
                    "each of the form fields entered. You can also enter "
                    "a message here that will be included in the email."))

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
    label = models.CharField(_("Label"),
        max_length=settings.FORMS_LABEL_MAX_LENGTH)
    field_type = models.IntegerField(_("Type"), choices=fields.NAMES)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text=_("Comma separated options where applicable. If an option "
            "itself contains commas, surround the option with `backticks`."))
    default = models.CharField(_("Default value"), blank=True,
        max_length=settings.FORMS_FIELD_MAX_LENGTH)
    placeholder_text = models.CharField(_("Placeholder Text"), blank=True,
        max_length=100, editable=settings.FORMS_USE_HTML5)
    help_text = models.CharField(_("Help text"), blank=True, max_length=100)

    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        order_with_respect_to = "form"

    def __unicode__(self):
        return self.label

    def get_choices(self):
        """
        Parse a comma separated choice string into a list of choices taking
        into account quoted choices.
        """
        choice = ""
        (quote, unquote) = ("`", "`")
        quoted = False
        for char in self.choices:
            if not quoted and char == quote:
                quoted = True
            elif quoted and char == unquote:
                quoted = False
            elif char == "," and not quoted:
                choice = choice.strip()
                if choice:
                    yield choice, choice
                choice = ""
            else:
                choice += char
        choice = choice.strip()
        if choice:
            yield choice, choice

    def is_a(self, *args):
        """
        Helper that returns ``True`` if the field's type is given in any arg.
        """
        return self.field_type in args


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
    value = models.CharField(max_length=settings.FORMS_FIELD_MAX_LENGTH,
                             null=True)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")
