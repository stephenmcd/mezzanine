# -*- coding: utf-8 -*-

import re
import unicodedata

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode

from mezzanine.utils.importing import import_dotted_path


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
    Will convert input string into a slug. The `MEZZANINE_SLUGIFY` setting
    will be used if set (must be callable).
    Otherwise, a replacement for Django's slugify which allows unicode chars in
    slugs, for URLs in Chinese, Russian, etc. will.
    Adopted from https://github.com/mozilla/unicode-slugify/
    """
    _slugify = getattr(settings, "MEZZANINE_SLUGIFY")
    if _slugify:
        if callable(_slugify):
            return _slugify(s)
        elif isinstance(_slugify, basestring):
            return import_dotted_path(_slugify)(s)
        raise RuntimeError("Invalid MEZZANINE_SLUGIFY setting")
    else:
        chars = []
        for char in smart_unicode(s):
            cat = unicodedata.category(char)[0]
            if cat in "LN" or char in "-_~":
                chars.append(char)
            elif cat == "Z":
                chars.append(" ")
        return re.sub("[-\s]+", "-", "".join(chars).strip()).lower()
