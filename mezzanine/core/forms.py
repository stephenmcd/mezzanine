from __future__ import unicode_literals
from future.builtins import str

from uuid import uuid4

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.safestring import mark_safe

from mezzanine.conf import settings


class Html5Mixin(object):
    """
    Mixin for form classes. Adds HTML5 features to forms for client
    side validation by the browser, like a "required" attribute and
    "email" and "url" input types.
    """

    def __init__(self, *args, **kwargs):
        super(Html5Mixin, self).__init__(*args, **kwargs)
        if hasattr(self, "fields"):
            # Autofocus first field
            first_field = next(iter(self.fields.values()))
            first_field.widget.attrs["autofocus"] = ""

            for name, field in self.fields.items():
                if settings.FORMS_USE_HTML5:
                    if isinstance(field, forms.EmailField):
                        self.fields[name].widget.input_type = "email"
                    elif isinstance(field, forms.URLField):
                        self.fields[name].widget.input_type = "url"
                if field.required:
                    self.fields[name].widget.attrs["required"] = ""


class TinyMceWidget(forms.Textarea):
    """
    Setup the JS files and targetting CSS class for a textarea to
    use TinyMCE.
    """

    class Media:
        js = ("mezzanine/tinymce/tinymce.min.js", settings.TINYMCE_SETUP_JS)
        css = {'all': ("mezzanine/tinymce/tinymce.css",)}

    def __init__(self, *args, **kwargs):
        super(TinyMceWidget, self).__init__(*args, **kwargs)
        self.attrs["class"] = "mceEditor"


class OrderWidget(forms.HiddenInput):
    """
    Add up and down arrows for ordering controls next to a hidden
    form field.
    """

    @property
    def is_hidden(self):
        return False

    def render(self, *args, **kwargs):
        rendered = super(OrderWidget, self).render(*args, **kwargs)
        arrows = ["<img src='%sadmin/img/admin/arrow-%s.gif' />" %
            (settings.STATIC_URL, arrow) for arrow in ("up", "down")]
        arrows = "<span class='ordering'>%s</span>" % "".join(arrows)
        return rendered + mark_safe(arrows)


class DynamicInlineAdminForm(forms.ModelForm):
    """
    Form for ``DynamicInlineAdmin`` that can be collapsed and sorted
    with drag and drop using ``OrderWidget``.
    """

    class Media:
        js = ("mezzanine/js/%s" % settings.JQUERY_UI_FILENAME,
              "mezzanine/js/admin/dynamic_inline.js",)


class SplitSelectDateTimeWidget(forms.SplitDateTimeWidget):
    """
    Combines Django's ``SelectDateTimeWidget`` and ``SelectDateWidget``.
    """
    def __init__(self, attrs=None, date_format=None, time_format=None):
        date_widget = SelectDateWidget(attrs=attrs)
        time_widget = forms.TimeInput(attrs=attrs, format=time_format)
        forms.MultiWidget.__init__(self, (date_widget, time_widget), attrs)


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Wraps render with a CSS class for styling.
    """
    def render(self, *args, **kwargs):
        rendered = super(CheckboxSelectMultiple, self).render(*args, **kwargs)
        return mark_safe("<span class='multicheckbox'>%s</span>" % rendered)


def get_edit_form(obj, field_names, data=None, files=None):
    """
    Returns the in-line editing form for editing a single model field.
    """

    # Map these form fields to their types defined in the forms app so
    # we can make use of their custom widgets.
    from mezzanine.forms import fields
    widget_overrides = {
        forms.DateField: fields.DATE,
        forms.DateTimeField: fields.DATE_TIME,
        forms.EmailField: fields.EMAIL,
    }

    class EditForm(forms.ModelForm):
        """
        In-line editing form for editing a single model field.
        """

        app = forms.CharField(widget=forms.HiddenInput)
        model = forms.CharField(widget=forms.HiddenInput)
        id = forms.CharField(widget=forms.HiddenInput)
        fields = forms.CharField(widget=forms.HiddenInput)

        class Meta:
            model = obj.__class__
            fields = field_names.split(",")

        def __init__(self, *args, **kwargs):
            super(EditForm, self).__init__(*args, **kwargs)
            self.uuid = str(uuid4())
            for f in self.fields.keys():
                field_class = self.fields[f].__class__
                try:
                    widget = fields.WIDGETS[widget_overrides[field_class]]
                except KeyError:
                    pass
                else:
                    self.fields[f].widget = widget()
                css_class = self.fields[f].widget.attrs.get("class", "")
                css_class += " " + field_class.__name__.lower()
                self.fields[f].widget.attrs["class"] = css_class
                self.fields[f].widget.attrs["id"] = "%s-%s" % (f, self.uuid)
                if settings.FORMS_USE_HTML5 and self.fields[f].required:
                    self.fields[f].widget.attrs["required"] = ""

    initial = {"app": obj._meta.app_label, "id": obj.id,
               "fields": field_names, "model": obj._meta.object_name.lower()}
    return EditForm(instance=obj, initial=initial, data=data, files=files)
