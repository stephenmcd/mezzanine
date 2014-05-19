from __future__ import unicode_literals
from future.builtins import int

from collections import defaultdict

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import string_concat, ugettext_lazy as _
from django.template.defaultfilters import urlize

from mezzanine.conf import settings, registry, TRANSLATED
from mezzanine.conf.models import Setting

if TRANSLATED:
    from modeltranslation.utils import build_localized_fieldname


FIELD_TYPES = {
    bool: forms.BooleanField,
    int: forms.IntegerField,
    float: forms.FloatField,
}

HELP_MODELTRANSLATION = _(
        "This setting value is language dependent, "
        "update its value for every language you have defined.")


class SettingsForm(forms.Form):
    """
    Form for settings - creates a field for each setting in
    ``mezzanine.conf`` that is marked as editable.
    """

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        settings.use_editable()
        # Create a form field for each editable setting's from its type.
        for name in sorted(registry.keys()):
            setting = registry[name]
            translatable = TRANSLATED and setting["translatable"]
            if setting["editable"]:
                field_class = FIELD_TYPES.get(setting["type"], forms.CharField)
                help_text = setting["description"]
                if translatable:
                    help_text = string_concat(help_text, "\n\n¹",
                                              HELP_MODELTRANSLATION)
                kwargs = {
                    "label": setting["label"] + (translatable and "¹:" or ":"),
                    "required": setting["type"] in (int, float),
                    "initial": getattr(settings, name),
                    "help_text": self.format_help(help_text),
                }
                if setting["choices"]:
                    field_class = forms.ChoiceField
                    kwargs["choices"] = setting["choices"]
                self.fields[name] = field_class(**kwargs)
                css_class = field_class.__name__.lower()
                self.fields[name].widget.attrs["class"] = css_class

    def __iter__(self):
        """
        Calculate and apply a group heading to each field and order by the
        heading.
        """
        fields = list(super(SettingsForm, self).__iter__())
        group = lambda field: field.name.split("_", 1)[0].title()
        misc = _("Miscellaneous")
        groups = defaultdict(int)
        for field in fields:
            groups[group(field)] += 1
        for (i, field) in enumerate(fields):
            setattr(fields[i], "group", group(field))
            if groups[fields[i].group] == 1:
                fields[i].group = misc
        return iter(sorted(fields, key=lambda x: (x.group == misc, x.group)))

    def save(self):
        """
        Save each of the settings to the DB.
        """
        for (name, value) in self.cleaned_data.items():
            setting_obj, created = Setting.objects.get_or_create(name=name)
            if TRANSLATED and not registry[name]["translatable"]:
                # Duplicate the value of the setting for every language
                for code, l in settings.LANGUAGES:
                    setattr(setting_obj,
                            build_localized_fieldname('value', code),
                            value)
            else:
                setting_obj.value = value
            setting_obj.save()

    def format_help(self, description):
        """
        Format the setting's description into HTML.
        """
        for bold in ("``", "*"):
            parts = []
            if description is None:
                description = ""
            for i, s in enumerate(description.split(bold)):
                parts.append(s if i % 2 == 0 else "<b>%s</b>" % s)
            description = "".join(parts)
        return mark_safe(urlize(description).replace("\n", "<br>"))
