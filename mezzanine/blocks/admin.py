from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from mezzanine.conf import settings
from mezzanine.blocks.models import Block, RichTextBlock

class BlockAdmin(admin.ModelAdmin):
    ordering = ['title', ]
    list_display = ('title', 'login_required', 'show_title')
    search_fields = ('title', 'content')

    fieldsets = (
        (None, {
            "fields": ["title", "content", ],
        }),
        (_("Advanced data"), {
            "fields": ['login_required', 'show_title', "slug" ],
            "classes": ("collapse-closed",)
        }),
    )

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "blocks.Block" in items:
                return True
        return False

class RichTextBlockAdmin(admin.ModelAdmin):
    ordering = ['title', ]
    list_display = ('title', 'login_required', 'show_title')
    search_fields = ('title', 'content')

    fieldsets = (
        (None, {
            "fields": ["title", "content", ],
        }),
        (_("Advanced"), {
            "fields": ['login_required', 'show_title', "slug"],
            "classes": ("collapse-closed",)
        }),
    )

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "blocks.RichTextBlock" in items:
                return True
        return False

admin.site.register(Block, BlockAdmin)
admin.site.register(RichTextBlock, RichTextBlockAdmin)
