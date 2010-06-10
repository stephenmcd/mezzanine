
from django.contrib import admin

from mezzanine.pages.models import Page
from mezzanine.core.admin import DisplayableAdmin


class PageAdmin(DisplayableAdmin):
    # Add the parent field and its class which will be hidden via CSS.
    fieldsets = DisplayableAdmin.fieldsets + (("parent", {"fields": 
        ("parent",), "classes": ("hidden-parent-fieldset",)}),)

admin.site.register(Page, PageAdmin)
