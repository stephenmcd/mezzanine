"""
Utils for working with static files.
"""
from __future__ import unicode_literals

from django.contrib.admin.templatetags.admin_static import static
from django.conf import settings
from django.utils.functional import lazy
from django.utils import six

# The 'static' template tag returns cache-busting file names, which prevents
# CDN's or browsers from serving old assets.
# See https://github.com/stephenmcd/mezzanine/pull/1411 for original
# proposal.
static_lazy = lazy(static, six.text_type)

# The above however is incompatible with Django's ManifestStaticFilesStorage
# (see https://github.com/stephenmcd/mezzanine/issues/1772), so in that
# case, this function is a no-op.
storage = getattr(settings, "STATICFILES_STORAGE", "")
if storage.endswith("ManifestStaticFilesStorage"):
    static_lazy = lambda s: s
