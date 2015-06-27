from __future__ import unicode_literals
from future.builtins import int, str

from collections import defaultdict

from mezzanine.conf import settings
from mezzanine.twitter import (QUERY_TYPE_USER, QUERY_TYPE_LIST,
                               QUERY_TYPE_SEARCH)
from mezzanine.twitter.models import Tweet, TwitterQueryException
from mezzanine import template


register = template.Library()


def tweets_for(query_type, args, per_user=None):
    """
    Retrieve tweets for a user, list or search term. The optional
    ``per_user`` arg limits the number of tweets per user, for
    example to allow a fair spread of tweets per user for a list.
    """
    lookup = {"query_type": query_type, "value": args[0]}
    try:
        tweets = Tweet.objects.get_for(**lookup)
    except TwitterQueryException:
        return []
    if per_user is not None:
        _tweets = defaultdict(list)
        for tweet in tweets:
            if len(_tweets[tweet.user_name]) < per_user:
                _tweets[tweet.user_name].append(tweet)
        tweets = sum(_tweets.values(), [])
        tweets.sort(key=lambda t: t.created_at, reverse=True)
    if len(args) > 1 and str(args[-1]).isdigit():
        tweets = tweets[:int(args[-1])]
    return tweets


@register.as_tag
def tweets_for_user(*args):
    """
    Tweets for a user.
    """
    return tweets_for(QUERY_TYPE_USER, args)


@register.as_tag
def tweets_for_list(*args):
    """
    Tweets for a user's list.
    """
    return tweets_for(QUERY_TYPE_LIST, args, per_user=1)


@register.as_tag
def tweets_for_search(*args):
    """
    Tweets for a search query.
    """
    return tweets_for(QUERY_TYPE_SEARCH, args)


@register.as_tag
def tweets_default(*args):
    """
    Tweets for the default settings.
    """
    query_type = settings.TWITTER_DEFAULT_QUERY_TYPE
    args = (settings.TWITTER_DEFAULT_QUERY,
            settings.TWITTER_DEFAULT_NUM_TWEETS)
    per_user = None
    if query_type == QUERY_TYPE_LIST:
        per_user = 1
    return tweets_for(query_type, args, per_user=per_user)
