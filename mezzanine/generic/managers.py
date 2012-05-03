
from django.contrib.comments.managers import CommentManager as DjangoCM

from mezzanine.conf import settings
from mezzanine.core.managers import CurrentSiteManager


class CommentManager(CurrentSiteManager, DjangoCM):
    """
    Provides filter for restricting comments that are not approved
    if ``COMMENTS_UNAPPROVED_VISIBLE`` is set to ``False``.
    """

    def visible(self):
        """
        Return the comments that are visible based on the
        ``COMMENTS_XXX_VISIBLE`` settings. When these settings
        are set to ``True``, the relevant comments are returned
        that shouldn't be shown, and are given placeholders in
        the template ``generic/includes/comment.html``.
        """
        settings.use_editable()
        visible = self.all()
        if not settings.COMMENTS_UNAPPROVED_VISIBLE:
            visible = visible.filter(is_public=True)
        if not settings.COMMENTS_REMOVED_VISIBLE:
            visible = visible.filter(is_removed=False)
        return visible

    def count_queryset(self):
        """
        Called from ``CommentsField.related_items_changed`` to store
        the comment count against an item each time a comment is saved.
        """
        return self.visible().count()


class KeywordManager(CurrentSiteManager):
    """
    Provides natural key method.
    """
    def get_by_natural_key(self, value):
        return self.get(value=value)
