from __future__ import unicode_literals

import os

from django.template.loaders import filesystem

from mezzanine.utils.sites import host_theme_path


class Loader(filesystem.Loader):
    """
    Template loader that implements host detection.
    """
    def get_dirs(self):
        theme_dir = host_theme_path()
        if theme_dir:
            return [os.path.join(theme_dir, "templates")]
        return []
