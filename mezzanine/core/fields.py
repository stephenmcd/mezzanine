
from django.core.exceptions import ImproperlyConfigured
from django.db.models import TextField
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.utils.importing import import_dotted_path


class HtmlField(TextField):
    """
    TextField that stores HTML.
    """

    def formfield(self, **kwargs):
        """
        Apply the widget class defined by the ``HTML_WIDGET_CLASS`` setting.
        """
        try:
            widget_class = import_dotted_path(settings.HTML_WIDGET_CLASS)
        except ImportError:
            raise ImproperlyConfigured(_("Could not import the value of "
                "settings.HTML_WIDGET_CLASS: %s" % settings.HTML_WIDGET_CLASS))
        kwargs["widget"] = widget_class()
        formfield = super(HtmlField, self).formfield(**kwargs)
        return formfield


# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(rules=[((HtmlField,), [], {})],
                                      patterns=["mezzanine\.core\.fields\."])
    except ImportError:
        pass
