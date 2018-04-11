from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.apps import AppConfig


class CoreConfig(AppConfig):

    name = 'mezzanine.core'

    def ready(self):
        from . import checks  # noqa

        if DJANGO_VERSION < (1, 9):
            # add_to_builtins was removed in 1.9 and replaced with a
            # documented public API configured by the TEMPLATES setting.
            from django.template.base import add_to_builtins
            add_to_builtins("mezzanine.template.loader_tags")
