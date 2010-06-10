
from django.db.models import Manager

from mezzanine.settings import COMMENTS_UNAPPROVED_VISIBLE


class CommentManager(Manager):
    """
    Provides filter for restricting comments that are not approved if 
    COMMENTS_UNAPPROVED_VISIBLE is set to False.
    """

    def visible(self):
        if COMMENTS_UNAPPROVED_VISIBLE:
            return self.all()
        return self.filter(approved=True)
