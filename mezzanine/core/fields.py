
from bleach import clean
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.conf import settings

from mezzanine.utils.importing import import_dotted_path


class RichTextField(models.TextField):
    """
    TextField that stores HTML.
    """

    def formfield(self, **kwargs):
        """
        Apply the widget class defined by the
        ``RICHTEXT_WIDGET_CLASS`` setting.
        """
        from mezzanine.conf import settings
        try:
            widget_class = import_dotted_path(settings.RICHTEXT_WIDGET_CLASS)
        except ImportError:
            raise ImproperlyConfigured(_("Could not import the value of "
                                         "settings.RICHTEXT_WIDGET_CLASS: %s"
                                         % settings.RICHTEXT_WIDGET_CLASS))
        kwargs["widget"] = widget_class()
        formfield = super(RichTextField, self).formfield(**kwargs)
        return formfield

    def clean(self, value, model_instance):
        """
        Remove potentially dangerous HTML tags and attributes.
        """
        return clean(value, settings.RICHTEXT_ALLOWED_TAGS,
                            settings.RICHTEXT_ALLOWED_ATTRIBUTES)


# Define a ``FileField`` that maps to filebrowser's ``FileBrowseField``
# if available, falling back to Django's ``FileField`` otherwise.
try:
    FileBrowseField = import_dotted_path("%s.fields.FileBrowseField" %
                                         settings.PACKAGE_NAME_FILEBROWSER)
except ImportError:
    FileField = models.FileField
else:
    class FileField(FileBrowseField):
        def __init__(self, *args, **kwargs):
            kwargs.pop("upload_to", "")
            super(FileField, self).__init__(*args, **kwargs)


HtmlField = RichTextField  # For backward compatibility in south migrations.

# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(rules=[((FileField, RichTextField,), [], {})],
            patterns=["mezzanine\.core\.fields\.",
                      "mezzanine\.generic\.fields\."])
    except ImportError:
        pass
