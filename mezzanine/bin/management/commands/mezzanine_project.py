from os import path

from django.core.management.commands.startproject import Command as BaseCommand
from django.utils.crypto import get_random_string

import mezzanine


class Command(BaseCommand):
    help = BaseCommand.help.replace("Django", "Mezzanine")

    def handle(self, project_name=None, target=None, *args, **options):
        """Overridden to provide a template value for nevercache_key. The
        method is copied verbatim from startproject.Command."""

        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        options['nevercache_key'] = get_random_string(50, chars)

        super(Command, self).handle(project_name, target, **options)

    def handle_template(self, template, subdir):
        """Use Mezzanine's project template by default. The method of picking
        the default directory is copied from Django's TemplateCommand."""
        if template is None:
            return path.join(mezzanine.__path__[0], subdir)
        return super(Command, self).handle(template, subdir)
