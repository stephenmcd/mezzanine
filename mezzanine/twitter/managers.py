
from django.db.models import Manager


class TweetManager(Manager):
    """
    Manager that handles generating the initial ``Query`` instance
    for a user, list or search term.
    """

    def get_for(self, query_type, value):
        """
        Create a query and run it for the given arg if it doesn't exist, and
        return the tweets for the query.
        """
        from mezzanine.twitter.models import Query
        lookup = {"type": query_type, "value": value}
        query, created = Query.objects.get_or_create(**lookup)
        if created:
            query.run()
        elif not query.interested:
            query.interested = True
            query.save()
        return query.tweets.all()
