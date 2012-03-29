# -*- coding: utf-8 -*-

import unicodedata

from django.core.urlresolvers import reverse


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


def slugify(s):
    """
    Replacement for Django's slugify which allows unicode chars in
    slugs, for URLs in Chinese, Russian, etc.
    """
    return (u''.join((c for c in unicodedata.normalize(u'NFKD', s).lower()
            if unicodedata.category(c) != u'Mn')))
