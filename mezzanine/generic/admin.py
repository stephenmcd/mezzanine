from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.generic.models import ThreadedComment


class ThreadedCommentAdmin(CommentsAdmin):
    """
    Admin class for comments.
    """

    list_display = ("avatar_link", "intro", "submit_date", "is_public",
                    "is_removed", "admin_link")
    list_display_links = ("intro", "submit_date")
    list_filter = [f for f in CommentsAdmin.list_filter if f != "site"]
    fieldsets = (
        (_("User"), {"fields": ("user_name", "user_email", "user_url")}),
        (None, {"fields": ("comment", ("is_public", "is_removed"))}),
    )

    def get_actions(self, request):
        actions = super(CommentsAdmin, self).get_actions(request)
        actions.pop("delete_selected")
        actions.pop("flag_comments")
        return actions

    # Disable the 'Add' action for this model, fixed a crash if you try
    # to create a comment from admin panel
    def has_add_permission(self, request):
        return False


generic_comments = getattr(settings, "COMMENTS_APP", "") == "mezzanine.generic"
if generic_comments and not settings.COMMENTS_DISQUS_SHORTNAME:
    admin.site.register(ThreadedComment, ThreadedCommentAdmin)
