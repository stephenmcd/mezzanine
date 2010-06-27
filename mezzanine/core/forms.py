
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class OrderWidget(forms.HiddenInput):

    def render(self, *args, **kwargs):
        rendered = super(OrderWidget, self).render(*args, **kwargs)
        arrows = ["<img src='%simg/admin/arrow-%s.gif' />" % 
            (settings.ADMIN_MEDIA_PREFIX, arrow) for arrow in ("up", "down")]
        arrows = "<span class='ordering'>%s</span>" % "".join(arrows)
        return rendered + mark_safe(arrows) 

class OrderableAdminForm(forms.ModelForm):
    _order = forms.CharField(label=_("Order"), widget=OrderWidget, 
        required=False)

