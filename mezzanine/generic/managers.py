
from django.db.models import Manager


class CommentManager(Manager):
    """
    Provides filter for restricting comments that are not approved if
    ``COMMENTS_UNAPPROVED_VISIBLE`` is set to ``False``.
    """

    def visible(self):
        from mezzanine.conf import settings
        settings.use_editable()
        visible = self.all()
        if not settings.COMMENTS_UNAPPROVED_VISIBLE:
            visible = visible.filter(is_public=True)
        if not settings.COMMENTS_REMOVED_VISIBLE:
            visible = visible.filter(is_removed=False)
        return visible

    def count_queryset(self):
        """
        Called from 
        ``mezzanine.generic.managers.GenericRelationWithCount.save_count`` 
        to store the comment count against an item each time a comment 
        is saved.
        """
        return self.visible().count()
