
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine.settings import CONTENT_MEDIA_URL


# Build the list of Mezzanine admin JS file. For Django 1.2 or later, include a 
# backport of the collapse js which targets the earlier admin.
ADMIN_JS = ["tinymce_setup.js", "jquery-1.4.2.min.js", "keywords_field.js"]
from django import VERSION
if not (VERSION[0] <= 1 and VERSION[1] <= 1):
    ADMIN_JS.append("collapse_backport.js")
ADMIN_JS = ["/%s/js/%s" % (CONTENT_MEDIA_URL.strip("/"), js) for js in ADMIN_JS]
ADMIN_JS.insert(0, "/media/admin/tinymce/jscripts/tiny_mce/tiny_mce.js")

class DisplayableAdmin(admin.ModelAdmin):

    class Media:
        js = ADMIN_JS
        
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {"fields": ("title", ("status", "publish_date"), "content")}),
        (_("Meta data"), {"fields": ("description", "keywords"), 
            "classes": ("collapse-closed",)},),
    )


