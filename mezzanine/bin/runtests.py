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

    django_path = os.path.dirname(os.path.abspath(django.__file__))
    django_test_settings_path = os.path.join(django_path,
                                             '../tests/test_sqlite.py')

    local_settings_path = os.path.join(project_path, "local_settings.py")
    test_settings_path = os.path.join(project_path, "test_settings.py")

    sys.path.insert(0, package_path)
    sys.path.insert(0, project_path)
    if not os.path.exists(test_settings_path):
        shutil.copy(local_settings_path + ".template", test_settings_path)
        with open(test_settings_path, "r") as f:
            local_settings = f.read()
        with open(django_test_settings_path, "r") as f:
            django_test_settings = '\n'.join(line for line in f.readlines()
                                             if not line.startswith('#'))
        with open(test_settings_path, "w") as f:
            test_reqs_str = """
from project_template import settings
globals().update(settings.__dict__)
if "mezzanine.accounts" not in settings.INSTALLED_APPS:
    INSTALLED_APPS = list(settings.INSTALLED_APPS) + ["mezzanine.accounts"]
"""
            f.write(test_reqs_str + local_settings + django_test_settings)

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
