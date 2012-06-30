
from django.core.management.base import NoArgsCommand

from mezzanine.twitter.models import Query


class Command(NoArgsCommand):
    """
    Polls the Twitter API for tweets associated to the queries in templates.
    Note that query.run() expects to have query.interested set to True
    which is a side-effect of having a page accessed by a client.
    If it has not been accessed since the last poll then the tweets
    will not be updated.
    """
    def handle_noargs(self, **options):
        for query in Query.objects.filter(interested=True):
            query.run()
