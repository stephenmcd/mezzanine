
from django.db.models import Manager

from mezzanine.settings import load_settings


class CommentManager(Manager):
    """
    Provides filter for restricting comments that are not approved if
    ``COMMENTS_UNAPPROVED_VISIBLE`` is set to False.
    """

    def visible(self):
        mezz_settings = load_settings("COMMENTS_UNAPPROVED_VISIBLE")
        if mezz_settings.COMMENTS_UNAPPROVED_VISIBLE:
            return self.all()
        return self.filter(approved=True)
