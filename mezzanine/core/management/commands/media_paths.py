
import os.path

from django.core.management.base import NoArgsCommand

from mezzanine.conf import settings


class Command(NoArgsCommand):
    """
    Prints out each of the media paths that should be configued for a 
    live deployment.
    """
    def handle_noargs(self, **options):
        paths = (
            (settings.MEDIA_URL, settings.MEDIA_ROOT),
            (settings.ADMIN_MEDIA_PREFIX, settings.GRAPPELLI_MEDIA_PATH),
            (settings.CONTENT_MEDIA_URL, settings.CONTENT_MEDIA_PATH),
        )
        for alias, path in paths:
            print "\nAlias '%s' required which resides in:\n%s/" % (alias, 
                  os.path.dirname(os.path.abspath(path)))
        print

