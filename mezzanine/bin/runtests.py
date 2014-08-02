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

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_template.settings"
    package_path = path_for_import(package)
    project_path = os.path.join(package_path, "project_template")
    local_settings_path = os.path.join(project_path, "local_settings.py")

    sys.path.insert(0, package_path)
    sys.path.insert(0, project_path)

    if not os.path.exists(local_settings_path):
        shutil.copy(local_settings_path + ".template", local_settings_path)
        from django.conf import settings
        apps = list(settings.INSTALLED_APPS)
        if "mezzanine.accounts" not in apps:
            apps += ["mezzanine.accounts"]
        with open(local_settings_path, "a") as f:
            f.write("INSTALLED_APPS = %s" % apps)
        atexit.register(lambda: os.remove(local_settings_path))

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))


if __name__ == "__main__":
    main()
