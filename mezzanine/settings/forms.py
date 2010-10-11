
from django import forms
from django.utils.functional import Promise

from mezzanine.settings import defaults, load_settings
from mezzanine.settings.models import Setting


FIELD_TYPES = {
    bool: forms.BooleanField,
    int: forms.IntegerField,
}

class SettingsForm(forms.Form):
    """
    Form for settings - creates a field for each setting in 
    ``mezzanine.settings.defaults`` that is marked as editable.
    """

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        editable = []
        # Get the names of editable settings.
        for name in dir(defaults):
            attr = getattr(defaults, name)
            if isinstance(attr, defaults.Setting) and attr.editable:
                editable.append(name)
        # Load the editable settings.
        mezz_settings = load_settings(*editable)
        for name in editable:
            setting = getattr(defaults, name)
            value = getattr(mezz_settings, name)
            setting_type = type(setting.default)
            # Create the form field based on the type of the setting.
            field_class = FIELD_TYPES.get(setting_type, forms.CharField)
            self.fields[name] = field_class(label=setting.name, 
                help_text=setting.description, initial=value, required=False)
    
    def save(self):
        # Save each of the settings to the DB.
        for (field, value) in self.cleaned_data.items():
            setting_obj, created = Setting.objects.get_or_create(name=field)
            setting_obj.value = value
            setting_obj.save()

    def as_p(self):
        """
        Add a HTML tag to the help text so we can style it.
        """
        return self._html_output(
            normal_row = u"<p%(html_class_attr)s>%(label)s %(field)s%(help_text)s</p>",
            error_row = u"%s",
            row_ender = "</p>",
            help_text_html = u" <span class=\"help\">%s</span>",
            errors_on_separate_row = True)
