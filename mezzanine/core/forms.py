
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


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

    initial = {"app": obj._meta.app_label, "id": obj.id, "attr": attr,
        "model": obj._meta.object_name.lower()}
    return EditForm(instance=obj, initial=initial, data=data)
