from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.messages import info
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.encoding import force_text
except ImportError:
    # Backward compatibility for Py2 and Django < 1.5
    from django.utils.encoding import force_unicode as force_text

from mezzanine.conf.models import Setting
from mezzanine.conf.forms import SettingsForm
from mezzanine.utils.urls import admin_url


class SettingsAdmin(admin.ModelAdmin):
    """
    Admin class for settings model. Redirect add/change views to the list
    view where a single form is rendered for editing all settings.
    """

    class Media:
        css = {"all": ("mezzanine/css/admin/settings.css",)}

    def changelist_redirect(self):
        changelist_url = admin_url(Setting, "changelist")
        return HttpResponseRedirect(changelist_url)

    def add_view(self, *args, **kwargs):
        return self.changelist_redirect()

    def change_view(self, *args, **kwargs):
        return self.changelist_redirect()

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        settings_form = SettingsForm(request.POST or None)
        if settings_form.is_valid():
            settings_form.save()
            info(request, _("Settings were successfully updated."))
            return self.changelist_redirect()
        extra_context["settings_form"] = settings_form
        extra_context["title"] = u"%s %s" % (
            _("Change"), force_text(Setting._meta.verbose_name_plural))
        return super(SettingsAdmin, self).changelist_view(request,
                                                            extra_context)


admin.site.register(Setting, SettingsAdmin)
