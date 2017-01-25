"""
Utils for working with static files.
"""
from __future__ import unicode_literals

from django.contrib.admin.templatetags.admin_static import static
from django.utils.functional import lazy
from django.utils import six

# The 'static' template tag returns cache-busting file names, which prevents
# CDN's or browsers from serving old assets.
static_lazy = lazy(static, six.text_type)
