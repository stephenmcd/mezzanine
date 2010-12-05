
from uuid import uuid4

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.models import Orderable
from mezzanine.utils.urls import content_media_urls


class OrderWidget(forms.HiddenInput):
    """
    Add up and down arrows for ordering controls next to a hidden form field.
    """
    def render(self, *args, **kwargs):
        rendered = super(OrderWidget, self).render(*args, **kwargs)
        arrows = ["<img src='%simg/admin/arrow-%s.gif' />" %
            (settings.ADMIN_MEDIA_PREFIX, arrow) for arrow in ("up", "down")]
        arrows = "<span class='ordering'>%s</span>" % "".join(arrows)
        return rendered + mark_safe(arrows)


class DynamicInlineAdminForm(forms.ModelForm):
    """
    Form for ``DynamicInlineAdmin`` that can be collapsed and sorted with 
    drag and drop using ``OrderWidget``.
    """
    
    class Media:
        js = content_media_urls("js/jquery-ui-1.8.1.custom.min.js", 
                                "js/dynamic_inline.js",)

    def __init__(self, *args, **kwargs):
        super(DynamicInlineAdminForm, self).__init__(*args, **kwargs)
        if issubclass(self._meta.model, Orderable):
            self.fields["_order"] = forms.CharField(label=_("Order"), 
                widget=OrderWidget, required=False)


class SplitSelectDateTimeWidget(forms.SplitDateTimeWidget):
    """
    Combines Django's ``SelectDateTimeWidget`` and ``SelectDateWidget``.
    """
    def __init__(self, attrs=None, date_format=None, time_format=None):
        date_widget = SelectDateWidget(attrs=attrs)
        time_format = forms.SplitDateTimeWidget.time_format
        time_widget = forms.TimeInput(attrs=attrs, format=time_format)
        forms.MultiWidget.__init__(self, (date_widget, time_widget), attrs)


def get_edit_form(obj, field_names, data=None, files=None):
    """
    Returns the in-line editing form for editing a single model field.
    """

    formfield_overrides = (
        (forms.DateField, SelectDateWidget),
        (forms.DateTimeField, SplitSelectDateTimeWidget),
    )

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
                for (field_class, widget_class) in formfield_overrides:
                    if isinstance(self.fields[f], field_class):
                        attrs = {"class": field_class.__name__.lower()}
                        self.fields[f].widget = widget_class(attrs=attrs)
                self.fields[f].widget.attrs["id"] = "%s-%s" % (f, self.uuid)

    initial = {"app": obj._meta.app_label, "id": obj.id, 
               "fields": field_names, "model": obj._meta.object_name.lower()}
    return EditForm(instance=obj, initial=initial, data=data, files=files)
