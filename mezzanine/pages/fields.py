
from mezzanine.conf import settings
from mezzanine.core.fields import MultiChoiceField


class MenusField(MultiChoiceField):
    """
    ``MultiChoiceField`` for specifying which menus a page should
    appear in.
    """

    def __init__(self, *args, **kwargs):
        choices = [t[:2] for t in settings.PAGE_MENU_TEMPLATES]
        default = settings.PAGE_MENU_TEMPLATES_DEFAULT
        if default is None:
            default = [t[0] for t in choices]
        elif not default:
            default = None
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
