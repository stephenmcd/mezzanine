
from django.core.urlresolvers import reverse

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
