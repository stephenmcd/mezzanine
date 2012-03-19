#!/usr/bin/env python

from __future__ import with_statement
from distutils.dir_util import copy_tree
from optparse import OptionParser
import os
from shutil import move
from uuid import uuid4

from mezzanine.utils.importing import path_for_import


def create_project():
    """
    Copies the contents of the project_template directory to a new
    directory specified as an argument to the command line.
    """

    parser = OptionParser(usage="usage: %prog [options] project_name")
    parser.add_option("-a", "--alternate", dest="alt", metavar="PACKAGE",
        help="Alternate package to use, containing a project_template")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("project_name must be specified")
    project_name = args[0]
    if project_name.startswith("-"):
        parser.error("project_name cannot start with '-'")
    project_path = os.path.join(os.getcwd(), project_name)

    # Ensure the given directory name doesn't clash with an existing
    # Python package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    else:
        parser.error("'%s' conflicts with the name of an existing "
                     "Python module and cannot be used as a project "
                     "name. Please try another name." % project_name)

    # Create the list of packages to build from - at this stage it
    # should only be one or two names, mezzanine plus an alternate
    # package.
    packages = ["mezzanine"]
    if options.alt:
        packages.append(options.alt)
    for package_name in packages:
        try:
            __import__(package_name)
        except ImportError:
            parser.error("Could not import package '%s'" % package_name)

    # Build the project up copying over the project_template from
    # each of the packages. An alternate package will overwrite
    # files from Mezzanine.
    for package_name in packages:
        package_path = path_for_import(package_name)
        copy_tree(os.path.join(package_path, "project_template"), project_path)
        move(os.path.join(project_path, "local_settings.py.template"),
             os.path.join(project_path, "local_settings.py"))

    # Generate a unique SECREY_KEY for the project's setttings module.
    settings_path = os.path.join(os.getcwd(), project_name, "settings.py")
    with open(settings_path, "r") as f:
        data = f.read()
    with open(settings_path, "w") as f:
        secret_key = "%s%s%s" % (uuid4(), uuid4(), uuid4())
        f.write(data.replace("%(SECRET_KEY)s", secret_key))

    # Clean up pyc files.
    for (root, dirs, files) in os.walk(project_path, False):
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))

if __name__ == "__main__":
    create_project()
