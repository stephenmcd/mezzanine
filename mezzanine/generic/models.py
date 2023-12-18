from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.template.defaultfilters import truncatewords_html
from django.utils.html import format_html
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django_comments.models import Comment

from mezzanine.conf import settings
from mezzanine.core.models import Orderable, Slugged
from mezzanine.generic.fields import RatingField
from mezzanine.generic.managers import CommentManager, KeywordManager
from mezzanine.utils.models import get_user_model_name
from mezzanine.utils.sites import current_site_id


class ThreadedComment(Comment):
    """
    Extend the ``Comment`` model from ``django_comments`` to
    add comment threading. ``Comment`` provides its own site foreign key,
    so we can't inherit from ``SiteRelated`` in ``mezzanine.core``, and
    therefore need to set the site on ``save``. ``CommentManager``
    inherits from Mezzanine's ``CurrentSiteManager``, so everything else
    site related is already provided.
    """

    by_author = models.BooleanField(_("By the blog author"), default=False)
    replied_to = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        editable=False,
        related_name="comments",
    )
    rating = RatingField(verbose_name=_("Rating"))

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
        return f"{url}#comment-{self.id}"

    def save(self, *args, **kwargs):
        """
        Set the current site ID, and ``is_public`` based on the setting
        ``COMMENTS_DEFAULT_APPROVED``.
        """
        if not self.id:
            self.is_public = settings.COMMENTS_DEFAULT_APPROVED
            self.site_id = current_site_id()
        super().save(*args, **kwargs)

    ################################
    # Admin listing column methods #
    ################################

    def intro(self):
        return truncatewords_html(self.comment, 20)

    intro.short_description = _("Comment")

    def avatar_link(self):
        from mezzanine.core.templatetags.mezzanine_tags import gravatar_url

        return format_html(
            "<a href='mailto:{}'><img style='vertical-align:middle; "
            "margin-right:3px;' src='{}' />{}</a>",
            self.user_email,
            gravatar_url(self.email),
            self.user_name,
        )

    avatar_link.short_description = _("User")

    def admin_link(self):
        return format_html(
            "<a href='{}'>{}</a>", self.get_absolute_url(), gettext("View on site")
        )

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

    keyword = models.ForeignKey(
        "Keyword",
        on_delete=models.CASCADE,
        verbose_name=_("Keyword"),
        related_name="assignments",
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.CASCADE
    )
    object_pk = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")

    class Meta:
        order_with_respect_to = "content_object"

    def __str__(self):
        return str(self.keyword)


class Rating(models.Model):
    """
    A rating that can be given to a piece of content.
    """

    value = models.IntegerField(_("Value"))
    rating_date = models.DateTimeField(_("Rating date"), auto_now_add=True, null=True)
    content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.CASCADE
    )
    object_pk = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")
    user = models.ForeignKey(
        get_user_model_name(),
        on_delete=models.CASCADE,
        verbose_name=_("Rater"),
        null=True,
        related_name="%(class)ss",
    )

    class Meta:
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")

    def save(self, *args, **kwargs):
        """
        Validate that the rating falls between the min and max values.
        """
        valid = map(str, settings.RATINGS_RANGE)
        if str(self.value) not in valid:
            raise ValueError(
                "Invalid rating. {} is not in {}".format(self.value, ", ".join(valid))
            )
        super().save(*args, **kwargs)
