from __future__ import unicode_literals

from django.contrib import admin

from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from mezzanine.galleries import get_gallery_model, get_gallery_image_model
from mezzanine.utils.static import static_lazy as static


Gallery = get_gallery_model()
GalleryImage = get_gallery_image_model()


class GalleryImageInline(TabularDynamicInlineAdmin):
    model = GalleryImage


class GalleryAdmin(PageAdmin):

    class Media:
        css = {"all": (static("mezzanine/css/admin/gallery.css"),)}

    inlines = (GalleryImageInline,)


admin.site.register(Gallery, GalleryAdmin)
