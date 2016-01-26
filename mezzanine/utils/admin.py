from __future__ import unicode_literals

from django.contrib import admin
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from mezzanine.utils.urls import admin_url


class SingletonAdmin(admin.ModelAdmin):
    """
    Admin class for models that should only contain a single instance
    in the database. Redirect all views to the change view when the
    instance exists, and to the add view when it doesn't.
    """

    def handle_save(self, request, response):
        """
        Handles redirect back to the dashboard when save is clicked
        (eg not save and continue editing), by checking for a redirect
        response, which only occurs if the form is valid.
        """
        form_valid = isinstance(response, HttpResponseRedirect)
        if request.POST.get("_save") and form_valid:
            return redirect("admin:index")
        return response

    def add_view(self, *args, **kwargs):
        """
        Redirect to the change view if the singleton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            kwargs.setdefault("extra_context", {})
            kwargs["extra_context"]["singleton"] = True
            response = super(SingletonAdmin, self).add_view(*args, **kwargs)
            return self.handle_save(args[0], response)
        return redirect(admin_url(self.model, "change", singleton.id))

    def changelist_view(self, *args, **kwargs):
        """
        Redirect to the add view if no records exist or the change
        view if the singleton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except self.model.MultipleObjectsReturned:
            return super(SingletonAdmin, self).changelist_view(*args, **kwargs)
        except self.model.DoesNotExist:
            return redirect(admin_url(self.model, "add"))
        return redirect(admin_url(self.model, "change", singleton.id))

    def change_view(self, *args, **kwargs):
        """
        If only the singleton instance exists, pass ``True`` for
        ``singleton`` into the template which will use CSS to hide
        the "save and add another" button.
        """
        kwargs.setdefault("extra_context", {})
        kwargs["extra_context"]["singleton"] = self.model.objects.count() == 1
        response = super(SingletonAdmin, self).change_view(*args, **kwargs)
        return self.handle_save(args[0], response)
