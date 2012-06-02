
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.core.templatetags.mezzanine_tags import thumbnail
from mezzanine.generic.fields import CommentsField, RatingField

class BlogPost(Displayable, Ownable, RichText):
    """
    A blog post.
    """

    categories = models.ManyToManyField("BlogCategory",
                                        verbose_name=_("Categories"),
                                        blank=True, related_name="blogposts")
    allow_comments = models.BooleanField(verbose_name=_("Allow comments"),
                                         default=True)
    comments = CommentsField(verbose_name=_("Comments"))
    rating = RatingField(verbose_name=_("Rating"))
    featured_image = FileField(verbose_name=_("Featured Image"), null=True,
                               upload_to="blog", max_length=255, blank=True)

    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        ordering = ("-publish_date",)

    @models.permalink
    def get_absolute_url(self):
        url_name = "blog_post_detail"
        kwargs = {"slug": self.slug}
        if settings.BLOG_URLS_USE_DATE:
            url_name = "blog_post_detail_date"
            month = str(self.publish_date.month)
            if len(month) == 1:
                month = "0" + month
            kwargs.update({"month": month, "year": self.publish_date.year})
        return (url_name, (), kwargs)

    def thumb(self, image_size=50, noimage=''):
        """
        Default thumbnail. Normally used in admin models.
        """
        if settings.BLOG_USE_FEATURED_IMAGE:
            if self.featured_image:
                image_url = thumbnail(self.featured_image, image_size, image_size)
            else:
                image_url = noimage

            return u'<img src="%s%s" height="%s" width="%s" />' % (settings.MEDIA_URL, image_url, image_size, image_size)
        return None
    thumb.allow_tags        = True
    thumb.short_description = 'Thumbnail'

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
