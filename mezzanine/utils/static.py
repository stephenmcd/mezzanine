"""
Utils for working with static files.
"""
from __future__ import unicode_literals

from django.contrib.admin.templatetags.admin_static import static
from django.utils.functional import lazy


static_lazy = lazy(static, str)
