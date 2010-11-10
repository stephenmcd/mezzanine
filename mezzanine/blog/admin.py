
from copy import deepcopy

from django.contrib import admin

from mezzanine.blog.models import BlogPost, BlogCategory, Comment
from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


blogpost_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
blogpost_fieldsets[0][1]["fields"].insert(1, "category")
blogpost_fieldsets[0][1]["fields"].append("content")
blogpost_radio_fields = deepcopy(DisplayableAdmin.radio_fields)
blogpost_radio_fields["category"] = admin.HORIZONTAL


class BlogPostAdmin(DisplayableAdmin, OwnableAdmin):

    fieldsets = blogpost_fieldsets
    list_display = ("title", "user", "status", "admin_link")
    radio_fields = blogpost_radio_fields

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)


class BlogCategoryAdmin(admin.ModelAdmin):

    fieldsets = ((None, {"fields": ("title",)}),)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "blog.BlogCategory" in items:
                return True
        return False


class CommentAdmin(admin.ModelAdmin):

    list_display = ("avatar_link", "intro", "time_created", "approved",
        "blog_post", "admin_link")
    list_display_links = ("intro", "time_created")
    list_editable = ("approved",)
    list_filter = ("blog_post", "approved", "name")
    search_fields = ("name", "email", "body")
    date_hierarchy = "time_created"
    ordering = ("-time_created",)
    fieldsets = (
        (None, {"fields": (("name", "email", "website"), "body",
            ("ip_address", "approved"), ("blog_post", "replied_to"))}),
    )

admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogCategory, BlogCategoryAdmin)
if not settings.COMMENTS_DISQUS_SHORTNAME:
    admin.site.register(Comment, CommentAdmin)
