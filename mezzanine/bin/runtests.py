from __future__ import unicode_literals

import atexit
import os
import shutil
import sys

import django


def main(package="mezzanine"):
    """
    This is the main test function called via ``python setup.py test``.
    It's responsible for hacking the ``project_template`` dir into
    an actual project to test against.
    """

    from mezzanine.utils.importing import path_for_import

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_template.test_settings"
    package_path = path_for_import(package)
    project_path = os.path.join(package_path, "project_template")

    # Create local_settings.py so it is imported by settings.py
    local_settings_path = os.path.join(project_path, "local_settings.py")
    shutil.copy(local_settings_path + ".template", local_settings_path)

    test_settings_path = os.path.join(project_path, "test_settings.py")

    sys.path.insert(0, package_path)
    if not os.path.exists(test_settings_path):
        # Import all our normal settings, and make a few test-specific tweaks.
        # require Mezzanine's accounts app, use the md5 password hasher to
        # speed up tests, use in-memory databases, and define an "other" db.
        test_settings = """
from project_template import settings

globals().update(i for i in settings.__dict__.items() if i[0].isupper())

# Require the mezzanine.accounts app. We use settings.INSTALLED_APPS here so
# the syntax test doesn't complain about an undefined name.
if "mezzanine.accounts" not in settings.INSTALLED_APPS:
    INSTALLED_APPS = list(settings.INSTALLED_APPS) + ["mezzanine.accounts"]

# Use an in-memory database for tests.
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

# Use the MD5 password hasher by default for quicker test runs. SHA1 still
# needs to be turned on for the contrib.auth tests to pass in Django 1.4.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',
                    'django.contrib.auth.hashers.SHA1PasswordHasher')
"""

        with open(test_settings_path, "w") as f:
            f.write(test_settings)

        def cleanup_test_settings():
            for fn in [test_settings_path, local_settings_path]:
                os.remove(fn)
                os.remove(fn + 'c')
        atexit.register(cleanup_test_settings)

    if django.VERSION >= (1, 7):
        django.setup()

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))


if __name__ == "__main__":
    main()
