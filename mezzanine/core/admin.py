
from django.conf import settings
from django.db.models import AutoField
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from mezzanine.utils import content_media_urls
from mezzanine.core.forms import DynamicInlineAdminForm
from mezzanine.core.models import Orderable


# Build the list of admin JS file for ``Displayable`` models.
# For >= Django 1.2 include a backport of the collapse js which targets
# earlier versions of the admin.
# This needs to be done as an iterator so that reverse() is not called until it needs to be
class JS(object):
    js = None
    def __iter__(self):
        if not JS.js:
            JS.js = ["%stinymce/jscripts/tiny_mce/tiny_mce.js" % settings.ADMIN_MEDIA_PREFIX,
                     reverse('mezzanine_js')]
            js = ["js/tinymce_setup.js", "js/jquery-1.4.2.min.js",
                  "js/keywords_field.js"]
            from django import VERSION
            if not (VERSION[0] <= 1 and VERSION[1] <= 1):
                js.append("js/collapse_backport.js")
            JS.js.extend(content_media_urls(*js))
        for js in JS.js:
            yield js


class DisplayableAdmin(admin.ModelAdmin):
    """
    Admin class for subclasses of the abstract ``Displayable`` model.
    """

    class Media:
        js = JS()

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
