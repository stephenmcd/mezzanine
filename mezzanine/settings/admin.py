
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from mezzanine.settings.models import Setting
from mezzanine.settings.forms import SettingsForm


class SettingsAdmin(admin.ModelAdmin):
    """
    Admin class for settings model. Redirect add/change views to the list 
    view where a single form is rendered for editing all settings.
    """
    
    def changelist_redirect(self):
        app = Setting._meta.app_label
        name = Setting.__name__.lower()
        changelist_url = reverse("admin:%s_%s_changelist" % (app, name))
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
            return self.changelist_redirect()
        extra_context["settings_form"] = settings_form
        extra_context["title"] = _("Change %s" % 
            force_unicode(Setting._meta.verbose_name_plural))
        return super(SettingsAdmin, self).changelist_view(request, extra_context)

admin.site.register(Setting, SettingsAdmin)
