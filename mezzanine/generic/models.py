
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models
from django.template.defaultfilters import truncatewords_html
from django.utils.translation import ugettext, ugettext_lazy as _

from mezzanine.generic.managers import CommentManager, KeywordManager
from mezzanine.core.models import Slugged, Orderable
from mezzanine.conf import settings
from mezzanine.utils.sites import current_site_id


class ThreadedComment(Comment):
    """
    Extend the ``Comment`` model from ``django.contrib.comments`` to
    add comment threading. ``Comment`` provides its own site foreign key,
    so we can't inherit from ``SiteRelated`` in ``mezzanine.core``, and
    therefore need to set the site on ``save``. ``CommentManager``
    inherits from Mezzanine's ``CurrentSiteManager``, so everything else
    site related is already provided.
    """

    by_author = models.BooleanField(_("By the blog author"), default=False)
    replied_to = models.ForeignKey("self", null=True, editable=False,
                                   related_name="comments")

    objects = CommentManager()

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def get_absolute_url(self):
        """
        Use the URL for the comment's content object, with a URL hash
        appended that references the individual comment.
        """
        url = self.content_object.get_absolute_url()
        return "%s#comment-%s" % (url, self.id)

    def save(self, *args, **kwargs):
        """
        Set the current site ID, and ``is_public`` based on the setting
        ``COMMENTS_DEFAULT_APPROVED``.
        """
        if not self.id:
            from mezzanine.conf import settings
            self.is_public = settings.COMMENTS_DEFAULT_APPROVED
            self.site_id = current_site_id()
        super(ThreadedComment, self).save(*args, **kwargs)

    ################################
    # Admin listing column methods #
    ################################

    def intro(self):
        return truncatewords_html(self.comment, 20)
    intro.short_description = _("Comment")

    def avatar_link(self):
        from mezzanine.core.templatetags.mezzanine_tags import gravatar_url
        vars = (self.user_email, gravatar_url(self.email), self.user_name)
        return ("<a href='mailto:%s'><img style='vertical-align:middle; "
                "margin-right:3px;' src='%s' />%s</a>" % vars)
    avatar_link.allow_tags = True
    avatar_link.short_description = _("User")

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(),
                                        ugettext("View on site"))
    admin_link.allow_tags = True
    admin_link.short_description = ""

    # Exists for backward compatibility when the gravatar_url template
    # tag which took the email address hash instead of the email address.
    @property
    def email_hash(self):
        return self.email


class Keyword(Slugged):
    """
    Keywords/tags which are managed via a custom JavaScript based
    widget in the admin.
    """

    objects = KeywordManager()

    class Meta:
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keywords")


class AssignedKeyword(Orderable):
    """
    A ``Keyword`` assigned to a model instance.
    """

    keyword = models.ForeignKey("Keyword", related_name="assignments")
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_pk = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")

    class Meta:
        order_with_respect_to = "content_object"

    def __unicode__(self):
        return unicode(self.keyword)


RATING_RANGE = range(settings.RATINGS_MIN, settings.RATINGS_MAX + 1)


class Rating(models.Model):
    """
    A rating that can be given to a piece of content.
    """

    value = models.IntegerField(_("Value"))
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_pk = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")

    class Meta:
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")

    def save(self, *args, **kwargs):
        """
        Validate that the rating falls between the min and max values.
        """
        if self.value not in RATING_RANGE:
            raise ValueError("Invalid rating. %s is not within %s and %s" %
                             (self.value, RATING_RANGE[0], RATING_RANGE[-1]))
        super(Rating, self).save(*args, **kwargs)
