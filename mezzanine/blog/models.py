
from datetime import datetime
from hashlib import md5

from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import truncatewords_html
from django.utils.translation import ugettext, ugettext_lazy as _

from mezzanine.core.models import Displayable
from mezzanine.blog.managers import CommentManager
from mezzanine.settings import COMMENTS_DEFAULT_APPROVED


class BlogPost(Displayable):
    """
    A blog post.
    """

    user = models.ForeignKey("auth.User", verbose_name=_("Author"), 
        related_name="blog_posts")

    class Meta:
        verbose_name = "Blog post"
        verbose_name_plural = "Blog posts"
        ordering = ("-publish_date",)

    def get_absolute_url(self):
        return reverse("blog_post_detail", kwargs={"slug": self.slug})

class Comment(models.Model):
    """
    A comment against a blog post.
    """

    name = models.CharField(_("Name"), max_length=100, help_text=_("required"))
    email = models.EmailField(_("Email"), 
        help_text=_("required (not published)"))
    email_hash = models.CharField(_("Email hash"), max_length=100, blank=True)
    body = models.TextField(_("Comment"))
    website = models.URLField(_("Website"), blank=True, help_text=_("optional"))
    blog_post = models.ForeignKey("BlogPost", related_name="comments")
    approved = models.BooleanField(_("Approved"), 
        default=COMMENTS_DEFAULT_APPROVED)
    ip_address = models.IPAddressField(_("IP address"), blank=True)
    time_created = models.DateTimeField(_("Created at"), default=datetime.now)
    replied_to = models.ForeignKey("self", blank=True, null=True, 
        related_name="comments")

    objects = CommentManager()

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ("time_created",)

    def __unicode__(self):
        return self.body
        
    def get_absolute_url(self):
        return "%s#comment-%s" % (reverse("blog_post_detail", 
            kwargs={"slug": self.blog_post.slug}), self.id)

    def save(self, *args, **kwargs):
        if not self.email_hash:
            self.email_hash = md5(self.email).hexdigest()
        super(Comment, self).save(*args, **kwargs)

    ################################
    # Admin listing column methods #
    ################################

    def intro(self):
        return truncatewords_html(self.body, 20)
    intro.short_description = _("Comment")

    def avatar_link(self):
        from mezzanine.blog.templatetags.blog_tags import gravatar_url
        return "<a href='mailto:%s'><img style='vertical-align:middle;" \
            "margin-right:3px;' src='%s' />%s</a>" % (self.email, 
            gravatar_url(self.email_hash), self.name)
    avatar_link.allow_tags = True
    avatar_link.short_description = ""

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), 
            ugettext("View on site"))
    admin_link.allow_tags = True
    admin_link.short_description = ""

