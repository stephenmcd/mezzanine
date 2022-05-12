import os
from distutils.dir_util import copy_tree
from importlib import import_module
from shutil import move, rmtree
from tempfile import mkdtemp

from django.core.management import CommandError
from django.core.management.commands.startproject import Command as BaseCommand
from django.utils.crypto import get_random_string

import mezzanine


class Command(BaseCommand):

    help = BaseCommand.help.replace("Django", "Mezzanine")

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "-a",
            "--alternate",
            dest="alt",
            metavar="PACKAGE",
            help="Alternate package to use, containing a project_template",
        )

    def handle(self, *args, **options):

        # Overridden to provide a template value for nevercache_key. The
        # method is copied verbatim from startproject.Command.
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        options["nevercache_key"] = get_random_string(50, chars)

        # Indicate that local_settings.py.template should be rendered
        options["files"].append("local_settings.py.template")

        super().handle(*args, **options)

        target = options.get("target", None)
        name = options["name"]
        if target is None:
            target = options["directory"]

        project_dir = self.get_project_directory(name, target)
        project_app_dir = os.path.join(project_dir, name)

        # Now rename "local_settings.py.template" to "local_settings.py"
        path = os.path.join(project_app_dir, "local_settings.py.template")
        if os.path.exists(path):
            move(path, os.path.join(project_app_dir, "local_settings.py"))

        # Handle an alternate package to install from (Eg cartridge, drum)
        # We basically re-run handle, pulling in files from the package,
        # overwriting the ones already copied from Mezzanine.
        alt = options.pop("alt", "")
        if alt:
            options["template"] = str(
                os.path.join(
                    os.path.dirname(os.path.abspath(import_module(alt).__file__)),
                    "project_template",
                )
            )
            options["directory"] = mkdtemp()
            self.handle(*args, **options)
            copy_tree(options["directory"], project_dir)
            rmtree(options["directory"])

        # The project template dir in Mezzanine requires __init__.py so that
        # the documentation can be generated, but including it in new projects
        # causes issues with running tests under Python >= 3.7, so remove it.
        os.remove(os.path.join(project_dir, "__init__.py"))

    def get_project_directory(self, name, target):
        """
        This code is copied verbatim from Django's
        TemplateCommand.handle(), but with the directory creation
        code removed.
        """
        # if some directory is given, make sure it's nicely expanded.
        if target is None:
            top_dir = os.path.join(os.getcwd(), name)
        else:
            top_dir = os.path.abspath(os.path.expanduser(target))
            if not os.path.exists(top_dir):
                raise CommandError(
                    "Destination directory '%s' does not "
                    "exist, please create it first." % top_dir
                )

        return top_dir

    def handle_template(self, template, subdir):
        """
        Use Mezzanine's project template by default. The method of
        picking the default directory is copied from Django's
        TemplateCommand.
        """
        if template is None:
            return str(os.path.join(mezzanine.__path__[0], subdir))
        return super().handle_template(template, subdir)
