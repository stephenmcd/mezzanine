
from django.contrib import admin

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.core.admin import DisplayableAdmin
from mezzanine.settings import COMMENTS_DISQUS_SHORTNAME


class BlogPostAdmin(DisplayableAdmin):

    list_display = ("title", "user", "status", "admin_link")

    def save_form(self, request, form, change):
        """
        Set the author as the logged in user.
        """
        obj = form.save(commit=False)
        if obj.user_id is None:
            obj.user = request.user
        return super(BlogPostAdmin, self).save_form(request, form, change)

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
