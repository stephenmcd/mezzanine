from __future__ import unicode_literals

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
            d = tuple(default)
            default = lambda: d
        defaults = {"max_length": 100, "choices": choices, "default": default}
        defaults.update(kwargs)
        super(MenusField, self).__init__(*args, **defaults)


# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(patterns=["mezzanine\.pages\.fields\."],
                                rules=[((MenusField,), [], {})])
    except ImportError:
        pass
