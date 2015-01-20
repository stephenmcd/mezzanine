from __future__ import unicode_literals
import atexit
import os
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

# Use in-memory databases, and define an "other" db to make Django happy.
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'},
             'other': {'ENGINE': 'django.db.backends.sqlite3'}}

# Use the md5 password hasher for quicker test runs.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

# These just need to be defined as something.
SECRET_KEY = "django_tests_secret_key"
NEVERCACHE_KEY = "django_tests_nevercache_key"
"""

        with open(test_settings_path, "w") as f:
            f.write(test_settings)

        def cleanup_test_settings():
            os.remove(test_settings_path)
            os.remove(test_settings_path + 'c')
        atexit.register(cleanup_test_settings)

    if django.VERSION >= (1, 7):
        django.setup()

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))


if __name__ == "__main__":
    main()
