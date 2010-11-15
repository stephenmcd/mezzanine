
from django.db.models import TextField

from mezzanine.conf import settings


class HtmlField(TextField):
    """
    TextField that stores HTML.
    """

    def formfield(self, **kwargs):
        """
        Apply the class to the widget that will render the field as a
        TincyMCE Editor.
        """
        formfield = super(HtmlField, self).formfield(**kwargs)
        formfield.widget.attrs["class"] = "mceEditor"
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
