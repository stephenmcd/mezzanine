
from django import forms

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
                self.fields[name] = field_class(label=name, required=False,
                                            initial=getattr(settings, name), 
                                            help_text=setting["description"])
    
    def save(self):
        # Save each of the settings to the DB.
        for (name, value) in self.cleaned_data.items():
            setting_obj, created = Setting.objects.get_or_create(name=name)
            setting_obj.value = value
            setting_obj.save()

    def as_p(self):
        """
        Add a HTML tag to the help text so we can style it.
        """
        return self._html_output(
            normal_row=u"<p>%(label)s %(field)s%(help_text)s</p>",
            error_row=u"%s", row_ender="</p>",
            help_text_html=u" <span class=\"help\">%s</span>",
            errors_on_separate_row=True)
