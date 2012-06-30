
from django.core.management.base import NoArgsCommand
from django.db import models
from mezzanine.twitter.models import Query, Topic


class Command(NoArgsCommand):
    """
    Polls the Twitter API for tweets associated to the queries in templates.
    Temporarily mark each query item as "interested" since this is required
    to get query.run() to actually pick up the tweets.
    """
    def handle_noargs(self, **options):
        for query in Query.objects.annotate(n=models.Count('topic')).filter(n__gt=0):
            query.interested = True
            query.run()
            pass
        return
    pass
