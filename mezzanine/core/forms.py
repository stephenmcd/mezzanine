
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import HtmlField


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

class OrderableAdminForm(forms.ModelForm):
    """
    Form for admin orderable inlines that uses the ``OrderableWidget``.
    """
    _order = forms.CharField(label=_("Order"), widget=OrderWidget, 
        required=False)

class TinyMceWidget(forms.Textarea):
    """
    Adds the required class to a Textarea field for the TinyMCE editor.
    """
    def __init__(self, *args, **kwargs):
        super(TinyMceWidget, self).__init__(*args, **kwargs)
        self.attrs["class"] = "mceEditor"

def get_edit_form(obj, attr, data=None):
    """
    Returns the in-line editing form for editing a single model field.
    """

    class EditForm(forms.ModelForm):
        """
        In-line editing form for editing a single model field.
        """

        app = forms.CharField(widget=forms.HiddenInput)
        model = forms.CharField(widget=forms.HiddenInput)
        id = forms.CharField(widget=forms.HiddenInput)
        attr = forms.CharField(widget=forms.HiddenInput)

        class Meta:
            model = obj.__class__
            fields = (attr,)
        
        def __init__(self, *args, **kwargs):
            """
            Apply the ``TinyMceWidget`` to ``HtmlField``.
            """
            super(EditForm, self).__init__(*args, **kwargs)
            if isinstance(obj._meta.get_field_by_name(attr)[0], HtmlField):
                self.fields[attr].widget = TinyMceWidget()

    initial = {"app": obj._meta.app_label, "id": obj.id, "attr": attr, 
        "model": obj._meta.object_name.lower()}
    return EditForm(instance=obj, initial=initial, data=data)
    
