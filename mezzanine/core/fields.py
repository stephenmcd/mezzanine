
from django.core.exceptions import ImproperlyConfigured
from django.db.models import TextField
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings


class HtmlField(TextField):
    """
    TextField that stores HTML.
    """

    def formfield(self, **kwargs):
        """
        Apply the widget class defined by the ``HTML_WIDGET_CLASS`` setting.
        """
        try:
            parts = settings.HTML_WIDGET_CLASS.rsplit(".", 1)
            widget_module_name, widget_class_name = parts
        except ValueError:
            raise ImproperlyConfigured(_("The setting HTML_WIDGET_CLASS "
                "must be a dotted package path to the widget class, eg: "
                "package_name.module_name.WidgetClassName"))
        try:
            widget_module = import_module(widget_module_name)
        except ImportError:
            raise ImproperlyConfigured(_("Could not import the module `%s` "
                "defined in the setting HTML_WIDGET_CLASS.") % 
                widget_module_name)
        try:
            widget_class = getattr(widget_module, widget_class_name)
        except AttributeError:
            raise ImproperlyConfigured(_("The widget class `%s` was not "
                "found in `%s` defined in the setting HTML_WIDGET_CLASS.") %
                (widget_class_name, widget_module_name))
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
