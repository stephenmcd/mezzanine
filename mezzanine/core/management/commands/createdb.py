
from django.core.management.base import NoArgsCommand
from django.core.management.commands import syncdb

from mezzanine.conf import settings


class Command(NoArgsCommand):

    help = ("Performs initial Mezzanine installation by running Django's "
            "syncdb and South's migrations faked.")
    can_import_settings = True
    option_list = syncdb.Command.option_list

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 0))
        syncdb.Command().execute(**options)
        if settings.USE_SOUTH:
            try:
                from south.management.commands import migrate
            except ImportError:
                return
            if options.get("interactive"):
                confirm = raw_input("\nWould you like to fake initial "
                                    "migrations? (yes/no): ")
                while True:
                    if confirm == "yes":
                        break
                    elif confirm == "no":
                        return
                    confirm = raw_input("Please enter either 'yes' or 'no': ")
            if verbosity >= 1:
                print
                print "Faking initial migrations ..."
                print
            migrate.Command().execute(fake=True)
