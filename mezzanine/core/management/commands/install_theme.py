
from distutils.dir_util import copy_tree
from optparse import make_option
import os

from django.core.management.base import CommandError, LabelCommand

from mezzanine.conf import settings
from mezzanine.utils import path_for_import


class Command(LabelCommand):
    """
    Copies the templates and media files from a theme package into 
    the current project. 
    """

    option_list = LabelCommand.option_list + (
        make_option("--noinput", action="store_false", dest="interactive", 
            help="Tells Django to NOT prompt the user for input of any kind.", 
            default=True),
    )
    help = ("Copies the templates and media files from a theme package into "
            "the current project.")
    args = "[theme_name]"
    label = "theme name"
    can_import_settings = True

    def handle_label(self, theme_name, **options):
        """
        Copy the templates and media files for the given theme package into 
        the current project. 
        """
        try:
            theme_path = path_for_import(theme_name)
        except ImportError:
            raise CommandError("Could not import the theme: %s" % theme_name)
        copy_paths = (
            (os.path.join(theme_path, "templates"), 
                settings.TEMPLATE_DIRS[-1]),
            (os.path.join(theme_path, "media"), 
                settings.MEDIA_ROOT),
        )
        if options.get("interactive"):
            confirm = raw_input("""
Theme installation may overwrite existing template and media files.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """)
            if confirm != "yes":
                raise CommandError("Theme installation cancelled.")
        for (path_from, path_to) in copy_paths:
            if os.path.exists(path_from):
                copy_tree(path_from, path_to)
