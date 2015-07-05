from __future__ import unicode_literals

from django_comments.managers import CommentManager as DjangoCM

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

    def get_by_natural_key(self, value):
        """
        Provides natural key method.
        """
        return self.get(value=value)

    def get_or_create_iexact(self, **kwargs):
        """
        Case insensitive title version of ``get_or_create``. Also
        allows for multiple existing results.
        """
        lookup = dict(**kwargs)
        try:
            lookup["title__iexact"] = lookup.pop("title")
        except KeyError:
            pass
        try:
            return self.filter(**lookup)[0], False
        except IndexError:
            return self.create(**kwargs), True

    def delete_unused(self, keyword_ids=None):
        """
        Removes all instances that are not assigned to any object. Limits
        processing to ``keyword_ids`` if given.
        """
        if keyword_ids is None:
            keywords = self.all()
        else:
            keywords = self.filter(id__in=keyword_ids)
        keywords.filter(assignments__isnull=True).delete()
