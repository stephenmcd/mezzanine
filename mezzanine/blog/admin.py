
from copy import deepcopy

from django.contrib import admin

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


blogpost_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
blogpost_fieldsets[0][1]["fields"].insert(1, "categories")
blogpost_fieldsets[0][1]["fields"].append("content")
blogpost_fieldsets[0][1]["fields"].append("allow_comments")
if settings.BLOG_USE_FEATURED_IMAGE:
    blogpost_fieldsets[0][1]["fields"].insert(-2, "featured_image")


class BlogPostAdmin(DisplayableAdmin, OwnableAdmin):
    """
    Admin class for blog posts.
    """

    fieldsets = blogpost_fieldsets
    list_display = ("title", "user", "status", "admin_link")
    filter_horizontal = ("categories",)

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)


class BlogCategoryAdmin(admin.ModelAdmin):
    """
    Admin class for blog categories. Hides itself from the admin menu
    unless explicitly specified.
    """

    fieldsets = ((None, {"fields": ("title",)}),)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "blog.BlogCategory" in items:
                return True
        return False


admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogCategory, BlogCategoryAdmin)
