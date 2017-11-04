#!/usr/bin/env python
from __future__ import unicode_literals

import atexit
import os
import shutil
import sys

import django
from django.core.management import call_command


def main(package="mezzanine", args=()):
    """
    This is the main test function called via ``python setup.py test``.
    It's responsible for hacking the ``project_template`` dir into
    an actual project to test against.
    """

    from mezzanine.utils.importing import path_for_import
    package_path = path_for_import(package)
    project_path = os.path.join(package_path, "project_template")

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_name.test_settings"

    project_app_path = os.path.join(project_path, "project_name")

    local_settings_path = os.path.join(project_app_path, "local_settings.py")
    test_settings_path = os.path.join(project_app_path, "test_settings.py")

    sys.path.insert(0, package_path)
    sys.path.insert(0, project_path)

    if not os.path.exists(test_settings_path):
        shutil.copy(local_settings_path + ".template", test_settings_path)
        with open(test_settings_path, "r") as f:
            local_settings = f.read()
        with open(test_settings_path, "w") as f:
            test_settings = """

from . import settings

globals().update(i for i in settings.__dict__.items() if i[0].isupper())

# Require the mezzanine.accounts app. We use settings.INSTALLED_APPS here so
# the syntax test doesn't complain about an undefined name.
if "mezzanine.accounts" not in settings.INSTALLED_APPS:
    INSTALLED_APPS = list(settings.INSTALLED_APPS) + ["mezzanine.accounts"]

# Use the MD5 password hasher by default for quicker test runs.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

"""
            f.write(test_settings + local_settings)

        def cleanup_test_settings():
            import os  # Outer scope sometimes unavailable in atexit functions.
            for fn in [test_settings_path, test_settings_path + 'c']:
                try:
                    os.remove(fn)
                except OSError:
                    pass
        atexit.register(cleanup_test_settings)

    django.setup()

    from django.core.management.commands import test
    if django.VERSION < (1, 10):
        sys.exit(test.Command().execute(*args, verbosity=1))
    sys.exit(call_command(test.Command(), *args, verbosity=1))


if __name__ == "__main__":
    main(args=sys.argv[1:])
