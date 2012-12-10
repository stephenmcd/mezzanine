
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import AutoField
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.forms import DynamicInlineAdminForm
from mezzanine.core.models import (Orderable, SitePermission,
                                   CONTENT_STATUS_PUBLISHED)
from mezzanine.utils.urls import admin_url


class DisplayableAdmin(admin.ModelAdmin):
    """
    Admin class for subclasses of the abstract ``Displayable`` model.
    """

    list_display = ("title", "status", "admin_link")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("title", "content",)
    date_hierarchy = "publish_date"
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {
            "fields": ["title", "status", ("publish_date", "expiry_date")],
        }),
        (_("Meta data"), {
            "fields": ["_meta_title", "slug",
                       ("description", "gen_description"),
                        "keywords", "in_sitemap"],
            "classes": ("collapse-closed",)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Add validation for the content field - it's required if status
        is set to published. We patch this method onto the form to avoid
        problems that come up with trying to use a form class. See:
        https://bitbucket.org/stephenmcd/mezzanine/pull-request/23/
        allow-content-field-on-richtextpage-to-be
        """
        form = super(DisplayableAdmin, self).get_form(request, obj, **kwargs)

        def clean_content(form):
            status = form.cleaned_data.get("status")
            content = form.cleaned_data.get("content")
            if status == CONTENT_STATUS_PUBLISHED and not content:
                raise ValidationError(_("This field is required if status "
                                        "is set to published."))
            return content

        form.clean_content = clean_content
        return form


class BaseDynamicInlineAdmin(object):
    """
    Admin inline that uses JS to inject an "Add another" link which
    when clicked, dynamically reveals another fieldset. Also handles
    adding the ``_order`` field and its widget for models that
    subclass ``Orderable``.
    """

    form = DynamicInlineAdminForm
    extra = 20

    def __init__(self, *args, **kwargs):
        super(BaseDynamicInlineAdmin, self).__init__(*args, **kwargs)
        if issubclass(self.model, Orderable):
            fields = self.fields
            if not fields:
                fields = self.model._meta.fields
                exclude = self.exclude or []
                fields = [f.name for f in fields if f.editable and
                    f.name not in exclude and not isinstance(f, AutoField)]
            if "_order" in fields:
                del fields[fields.index("_order")]
                fields.append("_order")
            self.fields = fields


class TabularDynamicInlineAdmin(BaseDynamicInlineAdmin, admin.TabularInline):
    template = "admin/includes/dynamic_inline_tabular.html"


class StackedDynamicInlineAdmin(BaseDynamicInlineAdmin, admin.StackedInline):
    template = "admin/includes/dynamic_inline_stacked.html"

    def __init__(self, *args, **kwargs):
        """
        Stacked dynamic inlines won't work without grappelli
        installed, as the JavaScript in dynamic_inline.js isn't
        able to target each of the inlines to set the value of
        the order field.
        """
        grappelli_name = getattr(settings, "PACKAGE_NAME_GRAPPELLI")
        if grappelli_name not in settings.INSTALLED_APPS:
            error = "StackedDynamicInlineAdmin requires Grappelli installed."
            raise Exception(error)
        super(StackedDynamicInlineAdmin, self).__init__(*args, **kwargs)


class OwnableAdmin(admin.ModelAdmin):
    """
    Admin class for models that subclass the abstract ``Ownable``
    model. Handles limiting the change list to objects owned by the
    logged in user, as well as setting the owner of newly created
    objects to the logged in user.

    Remember that this will include the ``user`` field in the required
    fields for the admin change form which may not be desirable. The
    best approach to solve this is to define a ``fieldsets`` attribute
    that excludes the ``user`` field or simple add ``user`` to your
    admin excludes: ``exclude = ('user',)``
    """

    def save_form(self, request, form, change):
        """
        Set the object's owner as the logged in user.
        """
        obj = form.save(commit=False)
        if obj.user_id is None:
            obj.user = request.user
        return super(OwnableAdmin, self).save_form(request, form, change)

    def queryset(self, request):
        """
        Filter the change list by currently logged in user if not a
        superuser. We also skip filtering if the model for this admin
        class has been added to the sequence in the setting
        ``OWNABLE_MODELS_ALL_EDITABLE``, which contains models in the
        format ``app_label.object_name``, and allows models subclassing
        ``Ownable`` to be excluded from filtering, eg: ownership should
        not imply permission to edit.
        """
        opts = self.model._meta
        model_name = ("%s.%s" % (opts.app_label, opts.object_name)).lower()
        models_all_editable = settings.OWNABLE_MODELS_ALL_EDITABLE
        models_all_editable = [m.lower() for m in models_all_editable]
        qs = super(OwnableAdmin, self).queryset(request)
        if request.user.is_superuser or model_name in models_all_editable:
            return qs
        return qs.filter(user__id=request.user.id)


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


###########################################
# Site Permissions Inlines for User Admin #
###########################################

class SitePermissionInline(admin.TabularInline):
    model = SitePermission
    max_num = 1
    can_delete = False


class SitePermissionUserAdmin(UserAdmin):
    inlines = [SitePermissionInline]

admin.site.unregister(User)
admin.site.register(User, SitePermissionUserAdmin)
