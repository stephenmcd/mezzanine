from __future__ import unicode_literals
import multiprocessing as mp
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

        # What we want to do is add some INSTALLED_APPS to settings
        # when testing. We do this by copying over a local_settings.py
        # module, then deleting that when we're done via atexit.
        #
        # Now that's *kinda* hacky, but the fun hasn't started yet. In
        # order to get the current list of INSTALLED_APPS so that we
        # can append to it without having to hard code it entirely,
        # we need to read the *current* value of INSTALLED_APPS, which
        # means we need to import it - but by doing so, our
        # local_settings.py improt will be triggered, and we won't have
        # the chance to import the one we're about to write - so we do
        # the settings import/read and local_settings file write in
        # a separate process, which means by the time all the settings
        # importing *first* happens in the foreground process, the
        # local_settings.py file will have be written.
        #
        # This is up there in my worst hacks of all time. ¯\_(ツ)_/¯
        #
        # PS: We need to import the top-level multiprocessing module
        # otherwise we hit: http://bugs.python.org/issue15881#msg170215

        def set_apps(local_settings_path):
            from django.conf import settings
            apps = list(settings.INSTALLED_APPS)
            if "mezzanine.accounts" not in apps:
                apps += ["mezzanine.accounts"]
            with open(local_settings_path, "a") as f:
                f.write("INSTALLED_APPS = %s" % apps)

        proc = mp.Process(target=set_apps, args=(local_settings_path,))
        proc.start()
        proc.join()
        atexit.register(lambda: os.remove(local_settings_path))

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))


if __name__ == "__main__":
    main()
