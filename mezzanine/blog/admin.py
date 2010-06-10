
from django.contrib import admin

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.core.admin import DisplayableAdmin
from mezzanine.settings import COMMENTS_DISQUS_SHORTNAME


class BlogPostAdmin(DisplayableAdmin):

    list_display = ("title", "user", "status", "admin_link")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("title", "body",)
    date_hierarchy = "publish_date"

    def save_model(self, request, obj, form, change):
        """
        Set the author as the logged in user.
        """
        obj.user = request.user
        super(BlogPostAdmin, self).save_model(request, obj, form, change)

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
if not COMMENTS_DISQUS_SHORTNAME:
    admin.site.register(Comment, CommentAdmin)
