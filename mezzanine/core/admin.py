
from django.contrib import admin
from django.db.models import AutoField
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.forms import DynamicInlineAdminForm
from mezzanine.core.models import Orderable
from mezzanine.utils import content_media_urls, admin_url


# Build the list of admin JS file for ``Displayable`` models.
# For >= Django 1.2 include a backport of collapse.js which targets
# earlier versions of the admin.
displayable_js = ["js/tinymce_setup.js", "js/jquery-1.4.4.min.js",
    "js/keywords_field.js"]
from django import VERSION
if not (VERSION[0] <= 1 and VERSION[1] <= 1):
    displayable_js.append("js/collapse_backport.js")
displayable_js = content_media_urls(*displayable_js)
displayable_js.insert(0, "%s/jscripts/tiny_mce/tiny_mce.js" % 
                                                    settings.TINYMCE_URL)


class DisplayableAdmin(admin.ModelAdmin):
    """
    Admin class for subclasses of the abstract ``Displayable`` model.
    """

    class Media:
        js = displayable_js

    list_display = ("title", "status", "admin_link")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("title", "content",)
    date_hierarchy = "publish_date"
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {"fields": ["title", "status", 
            ("publish_date", "expiry_date"),]}),
        (_("Meta data"), {"fields": ("slug", "description", "keywords"),
            "classes": ("collapse-closed",)},),
    )

    def save_form(self, request, form, change):
        """
        Store the keywords as a single string into the ``_keywords`` field
        for convenient access when searching.
        """
        obj = form.save(commit=True)
        obj.set_searchable_keywords()
        return super(DisplayableAdmin, self).save_form(request, form, change)


class DynamicInlineAdmin(admin.TabularInline):
    """
    Admin inline that uses JS to inject an "Add another" link when when 
    clicked, dynamically reveals another fieldset. Also handles adding the 
    ``_order`` field and its widget for models that subclass ``Orderable``.
    """

    form = DynamicInlineAdminForm
    extra = 20
    template = "admin/includes/dynamic_inline.html"

    def __init__(self, *args, **kwargs):
        super(DynamicInlineAdmin, self).__init__(*args, **kwargs)
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


class OwnableAdmin(admin.ModelAdmin):
    """
    Admin class for models that subclass the abstract ``Ownable`` model.
    Handles limiting the change list to objects owned by the logged in user,
    as well as setting the owner of newly created objects to the logged in
    user.
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
        Filter the change list by currently logged in user if not a superuser.
        """
        qs = super(OwnableAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__id=request.user.id)


class SingletonAdmin(admin.ModelAdmin):
    """
    Admin class for models that should only contain a single instance in the 
    database. Redirect all views to the change view when the instance exists, 
    and to the add view when it doesn't.
    """

    def add_view(self, *args, **kwargs):
        """
        Redirect to the change view if the singlton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            return super(SingletonAdmin, self).add_view(*args, **kwargs)
        else:
            change_url = admin_url(self.model, "change", singleton.id)
            return HttpResponseRedirect(change_url)

    def changelist_view(self, *args, **kwargs):
        """
        Redirect to the add view if no records exist or the change view if 
        the singlton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except self.model.MultipleObjectsReturned:
            return super(SingletonAdmin, self).changelist_view(*args, **kwargs)
        except self.model.DoesNotExist:
            add_url = admin_url(model, "add")
            return HttpResponseRedirect(add_url)
        else:
            change_url = admin_url(self.model, "change", singleton.id)
            return HttpResponseRedirect(change_url)

    def change_view(self, request, object_id, extra_context=None):
        """
        If only the singleton instance exists, pass True for ``singleton`` 
        into the template which will use CSS to hide relevant buttons.
        """
        if extra_context is None:
            extra_context = {}
        try:
            self.model.objects.get()
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            pass
        else:
            extra_context["singleton"] = True
        return super(SingletonAdmin, self).change_view(request, object_id, 
                                                        extra_context)
