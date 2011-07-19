
import re
import unicodedata

from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode

from mezzanine.conf import settings


def admin_url(model, url, object_id=None):
    """
    Returns the URL for the given model and admin url name.
    """
    opts = model._meta
    url = "admin:%s_%s_%s" % (opts.app_label, opts.object_name.lower(), url)
    args = ()
    if object_id is not None:
        args = (object_id,)
    return reverse(url, args=args)


def content_media_urls(*paths):
    """
    Prefix the list of paths with the ``CONTENT_MEDIA_URL`` setting for
    internally hosted JS and CSS files.
    """
    media_url = settings.CONTENT_MEDIA_URL.strip("/")
    return ["/%s/%s" % (media_url, path) for path in paths]


def slugify(s):
    """
    Replacement for Django's slugify which allows unicode chars in
    slugs, for URLs in Chinese, Russian, etc.
    Adopted from https://github.com/mozilla/unicode-slugify/
    """
    chars = []
    for char in smart_unicode(s):
        cat = unicodedata.category(char)[0]
        if cat in "LN" or char in "-_~":
            chars.append(char)
        elif cat == "Z":
            chars.append(" ")
    return re.sub("[-\s]+", "-", "".join(chars).strip()).lower()


def static_urls(url_prefix, document_root):
    """
    Returns the ``urlpattern`` for serving static content from the given
    ``document_root`` over the given ``url_prefix``.
    """
    pattern = "^%s/(?P<path>.*)$" % url_prefix.strip("/")
    view = "django.views.static.serve"
    args = {"document_root": document_root}
    return (pattern, view, args)
