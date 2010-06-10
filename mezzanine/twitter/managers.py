
from django.db.models import Manager


class TweetManager(Manager):

    def get_for(self, user_name=None, list_name=None, search_term=None):
        """
        Create a query and run it for the given arg if it doesn't exist, and 
        return the tweets for the query.
        """
        if user_name is not None:
            type, value = "user", user_name
        elif list_name is not None:
            type, value = "list", list_name
        elif search_term is not None:
            type, value = "search", search_term
        else:
            return
        from twitter.models import Query
        query, created = Query.objects.get_or_create(type=type, value=value)
        if created:
            query.run()
        elif not query.interested:
            query.interested = True
            query.save()
        return query.tweets.all()

