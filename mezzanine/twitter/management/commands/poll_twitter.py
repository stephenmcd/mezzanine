
from django.core.management.base import NoArgsCommand

from mezzanine.twitter.models import Query


class Command(NoArgsCommand):
    """
    Polls the Twitter API for tweets associated to the queries in templates.
    """
    def handle_noargs(self, **options):
        for query in Query.objects.filter(interested=True):
            query.run()
