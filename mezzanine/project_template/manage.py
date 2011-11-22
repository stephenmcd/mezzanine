#!/usr/bin/env python

# When project_template is used as the actual project during Mezzanine
# development, insert the development path into sys.path so that the
# development version of Mezzanine is used rather than the installed
# version.
import os
import sys
project_path = os.path.dirname(os.path.abspath(__file__))
project_dir = project_path.split(os.sep)[-1]
if project_dir == "project_template":
    dev_path = os.path.abspath(os.path.join(project_path, "..", ".."))
    if dev_path not in sys.path:
        sys.path.insert(0, dev_path)
    from mezzanine.utils.importing import path_for_import
    mezzanine_path = path_for_import("mezzanine")
    assert os.path.abspath(os.path.join(mezzanine_path, "..")) == dev_path

# Corrects some pathing issues in various contexts, such as cron jobs.
os.chdir(project_path)

from django.core.management import execute_manager
try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the "
        "directory containing %r. It appears you've customized things.\n"
        "You'll have to run django-admin.py, passing it your settings "
        "module.\n(If the file settings.py does indeed exist, it's causing "
        "an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
