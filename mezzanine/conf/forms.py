
from collections import defaultdict

from django import forms
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings, registry
from mezzanine.conf.models import Setting


FIELD_TYPES = {
    bool: forms.BooleanField,
    int: forms.IntegerField,
}

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
            if setting["editable"]:
                field_class = FIELD_TYPES.get(setting["type"], forms.CharField)
                self.fields[name] = field_class(label=name+":", required=False,
                                            initial=getattr(settings, name), 
                                            help_text=setting["description"])

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
        return iter(sorted(fields, cmp=lambda x, y: cmp(x.group, y.group)))
    
    def save(self):
        # Save each of the settings to the DB.
        for (name, value) in self.cleaned_data.items():
            setting_obj, created = Setting.objects.get_or_create(name=name)
            setting_obj.value = value
            setting_obj.save()
