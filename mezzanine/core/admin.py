
from django.db.models import AutoField
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine.settings import CONTENT_MEDIA_URL
from mezzanine.core.forms import OrderableAdminForm


media_url = CONTENT_MEDIA_URL.strip("/")
content_media = lambda files: ["/%s/%s" % (media_url, f) for f in files]

# Build the list of admin JS file for ``Displayable`` models. For Django 1.2 or
# later, include a backport of the collapse js which targets the earlier admin.
displayable_js = ["js/tinymce_setup.js", "js/jquery-1.4.2.min.js",  
    "js/keywords_field.js"]
from django import VERSION
if not (VERSION[0] <= 1 and VERSION[1] <= 1):
    displayable_js.append("js/collapse_backport.js")
displayable_js = content_media(displayable_js)
displayable_js.insert(0, "/media/admin/tinymce/jscripts/tiny_mce/tiny_mce.js")

orderable_js = content_media(["js/jquery-1.4.2.min.js", 
    "js/jquery-ui-1.8.1.custom.min.js", "js/orderable_inline.js"])


class DisplayableAdmin(admin.ModelAdmin):
    """
    Admin model for subclasses of the abstract ``Displayable`` model.
    """

    class Media:
        js = displayable_js
        
    list_display = ("title", "status", "admin_link")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("title", "body",)
    date_hierarchy = "publish_date"
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {"fields": ("title", ("status", "publish_date"), "content")}),
        (_("Meta data"), {"fields": ("description", "keywords"), 
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

class OrderableAdmin(admin.ModelAdmin):
    """
    Admin model that handles inlines for models that subclass the abstract 
    ``Orderable`` model.
    """

    class Media:
        css = {"all": content_media(["css/orderable_inline.css"])}
        js = orderable_js
    
    def __init__(self, *args, **kwargs):
        """
        Set the form for each of the inlines, the extras that will be hidden 
        and also ensure the ``_order`` field is last.
        """
        for inline in self.inlines:
            inline.form = OrderableAdminForm
            inline.extra = 20
            fields = inline.fields
            if not fields:
                fields = inline.model._meta.fields
                exclude = inline.exclude or []
                fields = [f.name for f in fields if f.editable and 
                    f.name not in exclude and not isinstance(f, AutoField)]
            if "_order" in fields:
                del fields[fields.index("_order")]
                fields.append("_order")
            inline.fields = fields
        super(OrderableAdmin, self).__init__(*args, **kwargs)


