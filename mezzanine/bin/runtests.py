from __future__ import unicode_literals
import atexit
import os
import shutil
import sys


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

    local_settings_path = os.path.join(project_path, "local_settings.py")
    test_settings_path = os.path.join(project_path, "test_settings.py")

    sys.path.insert(0, package_path)
    sys.path.insert(0, project_path)
    if not os.path.exists(test_settings_path):
        shutil.copy(local_settings_path + ".template", test_settings_path)
        with open(test_settings_path, "r") as f:
            local_settings = f.read()
        with open(test_settings_path, "w") as f:
            f.write("""
from project_template import settings
globals().update(settings.__dict__)
INSTALLED_APPS = list(settings.INSTALLED_APPS) + ["mezzanine.accounts"]
""" + local_settings)
        atexit.register(lambda: os.remove(test_settings_path))

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))


if __name__ == "__main__":
    main()
