from __future__ import print_function
from __future__ import unicode_literals
from future.builtins import int
from future.builtins import input

from optparse import make_option

from django.core.management.base import NoArgsCommand, CommandError
from django.core.management.commands import syncdb
from django.db import connection

from mezzanine.core.management import install_optional_data
from mezzanine.conf import settings


class Command(NoArgsCommand):

    help = ("Performs initial Mezzanine installation by running Django's "
            "syncdb and South's migrations faked.")
    can_import_settings = True
    option_list = syncdb.Command.option_list + (
        make_option("--nodata", action="store_true", dest="nodata",
                    default=False, help="Do not add demo data"),)

    def handle_noargs(self, **options):
        verbosity = int(options.get("verbosity", 0))
        interactive = int(options.get("interactive", 0))
        no_data = int(options.get("nodata", 0))
        if "conf_setting" in connection.introspection.table_names():
            raise CommandError("Database already created, you probably "
                               "want the syncdb or migrate command")

        syncdb.Command().execute(**options)
        if not interactive and not no_data:
            install_optional_data(verbosity)
        if settings.USE_SOUTH:
            try:
                from south.management.commands import migrate
            except ImportError:
                return
            if interactive:
                confirm = input("\nSouth is installed for this project."
                                    "\nWould you like to fake initial "
                                    "migrations? (yes/no): ")
                while True:
                    if confirm == "yes":
                        break
                    elif confirm == "no":
                        return
                    confirm = input("Please enter either 'yes' or 'no': ")
            if verbosity >= 1:
                print()
                print("Faking initial migrations ...")
                print()
            migrate.Command().execute(fake=True)
