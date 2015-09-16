from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.templatetags.admin_static import static

from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from mezzanine.galleries.models import Gallery, GalleryImage


class GalleryImageInline(TabularDynamicInlineAdmin):
    model = GalleryImage


class GalleryAdmin(PageAdmin):

    class Media:
        css = {"all": (static("mezzanine/css/admin/gallery.css"),)}

    inlines = (GalleryImageInline,)


admin.site.register(Gallery, GalleryAdmin)
