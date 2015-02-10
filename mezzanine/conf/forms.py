from __future__ import unicode_literals
from future.builtins import int

from collections import defaultdict

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import activate, get_language, ugettext_lazy as _
from django.template.defaultfilters import urlize

from mezzanine.conf import settings, registry
from mezzanine.conf.models import Setting

if settings.USE_MODELTRANSLATION:
    from django.utils.datastructures import SortedDict
    from modeltranslation.utils import build_localized_fieldname


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

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        # Create a form field for each editable setting's from its type.
        active_language = get_language()
        for name in sorted(registry.keys()):
            setting = registry[name]
            if setting["editable"]:
                field_class = FIELD_TYPES.get(setting["type"], forms.CharField)
                if settings.USE_MODELTRANSLATION and setting["translatable"]:
                    for code in SortedDict(settings.LANGUAGES):
                        try:
                            activate(code)
                        except:
                            pass
                        else:
                            self._init_field(setting, field_class, name, code)
                else:
                    self._init_field(setting, field_class, name)
        activate(active_language)

    def _init_field(self, setting, field_class, name, code=None):
        """Initialize a field wether it is built with a
        custom name for a specific translation language
        or not.
        """
        settings.use_editable()
        kwargs = {
            "label": setting["label"] + ":",
            "required": setting["type"] in (int, float),
            "initial": getattr(settings, name),
            "help_text": self.format_help(setting["description"]),
        }
        if setting["choices"]:
            field_class = forms.ChoiceField
            kwargs["choices"] = setting["choices"]
        field_instance = field_class(**kwargs)
        code_name = ('_modeltranslation_' + code if code else '')
        self.fields[name + code_name] = field_instance
        css_class = field_class.__name__.lower()
        field_instance.widget.attrs["class"] = css_class
        if code:
            field_instance.widget.attrs["class"] += " modeltranslation"

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
        active_language = get_language()
        for (name, value) in self.cleaned_data.items():
            if name not in registry:
                name, code = name.rsplit('_modeltranslation_', 1)
            else:
                code = None
            setting_obj, created = Setting.objects.get_or_create(name=name)
            if settings.USE_MODELTRANSLATION:
                if registry[name]["translatable"]:
                    try:
                        activate(code)
                    except:
                        pass
                    finally:
                        setting_obj.value = value
                        activate(active_language)
                else:
                    # Duplicate the value of the setting for every language
                    for code in SortedDict(settings.LANGUAGES):
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
