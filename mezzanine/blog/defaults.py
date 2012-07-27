"""
Default settings for the ``mezzanine.blog`` app. Each of these can be
overridden in your project's settings module, just like regular
Django settings. The ``editable`` argument for each controls whether
the setting is editable via Django's admin.

Thought should be given to how a setting is actually used before
making it editable, as it may be inappropriate - for example settings
that are only read during startup shouldn't be editable, since changing
them would require an application reload.
"""

from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


register_setting(
    name="BLOG_BITLY_USER",
    label=_("bit.ly username"),
    description=_("Username for http://bit.ly URL shortening service."),
    editable=True,
    default="",
)

register_setting(
    name="BLOG_BITLY_KEY",
    label=_("bit.ly key"),
    description=_("Key for http://bit.ly URL shortening service."),
    editable=True,
    default="",
)

register_setting(
    name="BLOG_USE_FEATURED_IMAGE",
    description=_("Enable featured images in blog posts"),
    editable=False,
    default=False,
)

register_setting(
    name="BLOG_URLS_USE_DATE",
    label=_("Use date URLs"),
    description=_("If ``True``, URLs for blog post include the month and "
        "year. Eg: /blog/yyyy/mm/slug/"),
    editable=False,
    default=False,
)

register_setting(
    name="BLOG_POST_PER_PAGE",
    label=_("Blog posts per page"),
    description=_("Number of blog posts shown on a blog listing page."),
    editable=True,
    default=5,
)

register_setting(
    name="BLOG_SLUG",
    description=_("Slug of the page object for the blog."),
    editable=False,
    default="blog",
)
