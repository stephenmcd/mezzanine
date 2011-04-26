
from django.core.exceptions import ImproperlyConfigured
from django.db.models import TextField
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.utils.importing import import_dotted_path


class RichTextField(TextField):
    """
    TextField that stores HTML.
    """

    def formfield(self, **kwargs):
        """
        Apply the widget class defined by the
        ``RICHTEXT_WIDGET_CLASS`` setting.
        """
        try:
            widget_class = import_dotted_path(settings.RICHTEXT_WIDGET_CLASS)
        except ImportError:
            raise ImproperlyConfigured(_("Could not import the value of "
                                         "settings.RICHTEXT_WIDGET_CLASS: %s"
                                         % settings.RICHTEXT_WIDGET_CLASS))
        kwargs["widget"] = widget_class()
        formfield = super(RichTextField, self).formfield(**kwargs)
        return formfield


HtmlField = RichTextField # For backward compatibility in south migrations.

# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(rules=[((RichTextField,), [], {})],
            patterns=["mezzanine\.core\.fields\.",
                      "mezzanine\.generic\.fields\."])
    except ImportError:
        pass
