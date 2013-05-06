
def runtests():

    import os, sys, shutil, atexit
    from mezzanine.utils.importing import path_for_import

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_template.settings"
    mezz_path = path_for_import("mezzanine")
    sys.path.insert(0, mezz_path)

    project_path = os.path.join(mezz_path, "project_template")
    local_settings_path = os.path.join(project_path, "local_settings.py")
    if not os.path.exists(local_settings_path):
        shutil.copy(local_settings_path + ".template", local_settings_path)
        atexit.register(lambda: os.remove(local_settings_path))

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))
