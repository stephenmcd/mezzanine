
from collections import defaultdict
import datetime
import math

from django.utils.translation import ugettext, ungettext

from mezzanine import template
from mezzanine.twitter.models import Tweet


register = template.Library()


def tweets_for(type, args, per_user=None):
    """
    Retrieve tweets for a user, list or search term. The optional
    ``per_user`` arg limits the number of tweets per user, for example to
    allow a fair spread of tweets per user for a list.
    """
    lookup = {}
    lookup[type] = args[0].strip("\"'")
    tweets = Tweet.objects.get_for(**lookup)
    if per_user is not None:
        _tweets = defaultdict(list)
        for tweet in tweets:
            if len(_tweets[tweet.user_name]) < per_user:
                _tweets[tweet.user_name].append(tweet)
        tweets = sum(_tweets.values(), [])
        tweets.sort(key=lambda t: t.created_at, reverse=True)
    if len(args) > 1 and args[-1].isdigit():
        tweets = tweets[:int(args[-1])]
    return tweets


@register.as_tag
def tweets_for_user(*args):
    """
    Tweets for a user.
    """
    return tweets_for("user_name", args)


@register.as_tag
def tweets_for_list(*args):
    """
    Tweets for a user's list.
    """
    return tweets_for("list_name", args, per_user=1)


@register.as_tag
def tweets_for_search(*args):
    """
    Tweets for a search query.
    """
    return tweets_for("search_term", args)
