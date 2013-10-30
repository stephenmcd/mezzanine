
import os
from optparse import make_option

from django.conf import settings 
from django.core.management.base import BaseCommand, CommandError

from uuid import uuid4

class Command(NoArgsCommand):
    '''
    Used to generate a new SECRET_KEY and NEVERCACHE_KEY
    into local_settings.py. Run this command after
    deployment so that your new local_settings.py gets
    updated
    '''
    help = ("Creates new SECRET_KEY and NEVERCACHE_KEY into local_settings.py.")
    can_import_settings = True
    option_list = BaseCommand.option_list

    
    def handle_noargs(self, **options):
    # Generate a unique SECRET_KEY for the project's local_setttings module.
    settings_path = os.getcwd()
    with open(settings_path, "r") as f:
        data = f.read()
    with open(settings_path, "w") as f:
        make_key = lambda: "%s%s%s" % (uuid4(), uuid4(), uuid4())
        data = data.replace("%(SECRET_KEY)s", make_key())
        data = data.replace("%(NEVERCACHE_KEY)s", make_key())
        f.write(data)