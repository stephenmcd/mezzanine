
from itertools import groupby

from django import forms
from django.utils.safestring import mark_safe
from django.template.defaultfilters import urlize
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings, registry
from mezzanine.conf.models import Setting


FIELD_TYPES = {
    bool: forms.BooleanField,
    int: forms.IntegerField,
    float: forms.FloatField,
}


class SettingsForm(forms.Form):
    """
    Form for settings - creates a field for each setting in
    ``mezzanine.conf`` that is marked as editable.
    """
    order = {}

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        settings.use_editable()
        # Create a form field for each editable setting's from its type.
        for name in sorted(registry.keys()):
            setting = registry[name]
            if setting["editable"]:
                field_class = FIELD_TYPES.get(setting["type"], forms.CharField)
                kwargs = {
                    "label": setting["label"] + ":",
                    "required": setting["type"] in (int, float),
                    "initial": getattr(settings, name),
                    "help_text": self.format_help(setting["description"]),
                }
                if setting["choices"]:
                    field_class = forms.ChoiceField
                    kwargs["choices"] = setting["choices"]
                self.fields[name] = field_class(**kwargs)
                self.order[setting["name"]] = setting["order"]
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
        for (i, field) in enumerate(fields):
            setattr(fields[i], "group", group(field))

        group_fields = []
        misc_fields = []
        for key, valuesiter in groupby(fields, key=group):
            values = sorted(valuesiter, key=lambda x: self.order[x.name])
            if len(values) == 1:
                values[0].group = misc
                misc_fields += values
            else:
                group_fields += values

        return iter(group_fields + misc_fields)

    def save(self):
        """
        Save each of the settings to the DB.
        """
        for (name, value) in self.cleaned_data.items():
            setting_obj, created = Setting.objects.get_or_create(name=name)
            setting_obj.value = value
            setting_obj._order = self.order[name]
            setting_obj.save()

    def format_help(self, description):
        """
        Format the setting's description into HTML.
        """
        for bold in ("``", "*"):
            parts = []
            for i, s in enumerate(description.split(bold)):
                parts.append(s if i % 2 == 0 else "<b>%s</b>" % s)
            description = "".join(parts)
        return mark_safe(urlize(description).replace("\n", "<br>"))
