#!/usr/bin/env python
import sys

from django.conf import settings
from django.core import management


def create_project():
    # Put mezzanine.conf in INSTALLED_APPS so call_command can find
    # our command,
    settings.configure()
    settings.INSTALLED_APPS = list(settings.INSTALLED_APPS) + ['mezzanine.bin']
    argv = sys.argv[:1] + ['mezzanine_project'] + sys.argv[1:]
    management.execute_from_command_line(argv)


if __name__ == "__main__":
    create_project()
