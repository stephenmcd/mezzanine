
from django.db.models import Count, Manager

from mezzanine.settings import load_settings
from mezzanine.core.managers import DisplayableManager


class BlogPostManager(DisplayableManager):
    """
    Extends ``DisplayableManager.published`` with annotated comment counts.
    """
    
    def published(self, *args, **kwargs):
        return super(BlogPostManager, self).published(*args, **kwargs) \
            .annotate(num_comments=Count("comments")).select_related(depth=1)


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
