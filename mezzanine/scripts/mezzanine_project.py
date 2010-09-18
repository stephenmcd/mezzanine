#!/usr/bin/env python

from __future__ import with_statement
import os
from optparse import OptionParser
from distutils.dir_util import copy_tree
from shutil import move
from uuid import uuid4


def create_project():
    """
    Copies the contents of the project_template directory to a new directory
    specified as an argument to the command line.
    """

    parser = OptionParser(usage="usage: %prog [options] project_name")
    parser.add_option("-a", "--alternate", dest="alt", metavar="PACKAGE", 
        help="Alternate package to use, containing a project_template")
    parser.add_option("-s", "--source", dest="copy_source", default=False,
        action="store_true", help="Copy package source to new project")
    parser.add_option("-t", "--templates", dest="copy_templates", default=True,
        action="store_false", help="Copy templates to the project [default]")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("project_name must be specified")
    project_name = args[0]
    if project_name.startswith("-"):
        parser.error("project_name cannot start with '-'")

    # Ensure the given directory name doesn't clash with an existing Python
    # package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    else:
        parser.error("'%s' conflicts with the name of an existing "
            "Python module and cannot be used as a project name. Please try "
            "another name." % project_name)
    
    packages = ["mezzanine"]
    if options.alt:
        packages.append(options.alt)
    for package_name in packages:
        try:
            __import__(package_name)
        except ImportError:
            parser.error("Could not import package '%s'" % package) 
    for package_name in packages:
        package = __import__(package_name)
        package_path = os.path.dirname(os.path.abspath(package.__file__))
        from_path = os.path.join(package_path, "project_template")
        to_path = os.path.join(os.getcwd(), project_name)
        if options.copy_source:
            copy_tree(package_path, os.path.join(to_path, package_name))
        copy_tree(from_path, to_path)
        move(os.path.join(to_path, "local_settings.py.template"),
            os.path.join(to_path, "local_settings.py"))
        if options.copy_templates:
            to_path = os.path.join(to_path, "templates")
            for app_dir in os.listdir(package_path):
                template_dir = os.path.join(package_path, app_dir, "templates")
                if os.path.isdir(template_dir):
                    copy_tree(template_dir, to_path)
    settings_path = os.path.join(os.getcwd(), project_name, "settings.py")
    with open(settings_path, "r") as f:
        data = f.read()
    with open(settings_path, "w") as f:
        secret_key = "%s%s%s" % (uuid4(), uuid4(), uuid4())
        f.write(data.replace("%(SECRET_KEY)s", secret_key))


if __name__ == "__main__":
    create_project()

