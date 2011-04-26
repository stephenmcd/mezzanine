
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.generic.fields import CommentsField, RatingField


class BlogPost(Displayable, Ownable, RichText):
    """
    A blog post.
    """

    categories = models.ManyToManyField("BlogCategory", blank=True,
                                        related_name="blogposts")
    comments = CommentsField(verbose_name=_("Comments"))
    rating = RatingField(verbose_name=_("Rating"))

    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        ordering = ("-publish_date",)

    @models.permalink
    def get_absolute_url(self):
        return ("blog_post_detail", (), {"slug": self.slug})


class BlogCategory(Slugged):
    """
    A category for grouping blog posts into a series.
    """

    class Meta:
        verbose_name = _("Blog Category")
        verbose_name_plural = _("Blog Categories")

    @models.permalink
    def get_absolute_url(self):
        return ("blog_post_list_category", (), {"slug": self.slug})
