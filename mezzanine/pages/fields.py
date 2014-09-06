from __future__ import unicode_literals
from django.db import connection

from mezzanine.conf import settings
from mezzanine.core.fields import MultiChoiceField


class MenusField(MultiChoiceField):
    """
    ``MultiChoiceField`` for specifying which menus a page should
    appear in.
    """

    def __init__(self, *args, **kwargs):
        choices = [t[:2] for t in getattr(settings, "PAGE_MENU_TEMPLATES", [])]
        default = getattr(settings, "PAGE_MENU_TEMPLATES_DEFAULT", None)
        if default is None:
            default = [t[0] for t in choices]
        elif not default:
            default = None
        if isinstance(default, (tuple, list)):
            # Django seeing just a mutable default would force it to unicode.
            default = tuple(default)
        defaults = {"max_length": 100, "choices": choices, "default": default}
        defaults.update(kwargs)
        super(MenusField, self).__init__(*args, **defaults)

    def get_default(self):
        """
        Django's default behavior for `get_default` forces to unicode unless
        the field is callable, as referenced here:
        https://github.com/stephenmcd/mezzanine/commit/97a92f92

        But the purpose of this behavior was to prevent mutable values being
        passed as default, which the conversion to a tuple in __init__ already
        handles.

        Django 1.7 migrations do not allow lambdas in field definitions, so
        instead overwriting `get_default` to not require a callable.
        """
        if self.has_default():
            return self.default
        if (not self.empty_strings_allowed or (self.null and
                   not connection.features.interprets_empty_strings_as_nulls)):
            return None
        return ""


# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(patterns=["mezzanine\.pages\.fields\."],
                                rules=[((MenusField,), [], {})])
    except ImportError:
        pass
