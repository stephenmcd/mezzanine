from shutil import move
import django
from django.core.management import CommandError
from os import path

from django.core.management.commands.startproject import Command as BaseCommand
from django.utils import six
from django.utils.crypto import get_random_string
import os

import mezzanine


class Command(BaseCommand):
    help = BaseCommand.help.replace("Django", "Mezzanine")

    def handle(self, *args, **options):

        # Overridden to provide a template value for nevercache_key. The
        # method is copied verbatim from startproject.Command."""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        options['nevercache_key'] = get_random_string(50, chars)

        # Indicate that local_settings.py.template should be rendered
        options['files'] = ['local_settings.py.template']

        super(Command, self).handle(*args, **options)

        if django.VERSION < (1, 8):
            proj_name, target = args + (None,) * max(0, 2 - len(args))
        else:
            proj_name, target = options.pop('name'), options.pop('directory')

        project_dir = self.get_project_directory(proj_name, target)
        project_app_dir = os.path.join(project_dir, proj_name)

        # Now rename "local_settings.py.template" to "local_settings.py"
        move(os.path.join(project_app_dir, "local_settings.py.template"),
             os.path.join(project_app_dir, "local_settings.py"))

    def get_project_directory(self, name, target):
        """This code is copied verbatim from Django's TemplateCommand.handle(),
        but with the directory creation commented out."""

        # if some directory is given, make sure it's nicely expanded
        if target is None:
            top_dir = path.join(os.getcwd(), name)
            # try:
            #     os.makedirs(top_dir)
            # except OSError as e:
            #     if e.errno == errno.EEXIST:
            #         message = "'%s' already exists" % top_dir
            #     else:
            #         message = e
            #     raise CommandError(message)
        else:
            top_dir = os.path.abspath(path.expanduser(target))
            if not os.path.exists(top_dir):
                raise CommandError("Destination directory '%s' does not "
                                   "exist, please create it first." % top_dir)

        return top_dir

    def handle_template(self, template, subdir):
        """Use Mezzanine's project template by default. The method of picking
        the default directory is copied from Django's TemplateCommand."""
        if template is None:
            return six.text_type(path.join(mezzanine.__path__[0], subdir))
        return super(Command, self).handle_template(template, subdir)
