from __future__ import unicode_literals

def runtests():

    import os, sys, shutil, atexit
    from mezzanine.utils.importing import path_for_import

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_template.settings"
    mezz_path = path_for_import("mezzanine")
    project_path = os.path.join(mezz_path, "project_template")
    local_settings_path = os.path.join(project_path, "local_settings.py")

    sys.path.insert(0, mezz_path)
    sys.path.insert(0, project_path)

    if not os.path.exists(local_settings_path):
        shutil.copy(local_settings_path + ".template", local_settings_path)
        with open(local_settings_path, "a") as f:
            f.write("""

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.blog",
    "mezzanine.forms",
    "mezzanine.pages",
    "mezzanine.galleries",
    "mezzanine.twitter",
    "mezzanine.accounts",
    "mezzanine.mobile",
)

                """)
        atexit.register(lambda: os.remove(local_settings_path))

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))
