
from collections import defaultdict

from django import template

from mezzanine.core.templatetags.mezzanine_tags import register_as_tag
from mezzanine.twitter.models import Tweet


register = template.Library()


def tweets_for(type, args, per_user=None):
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

@register_as_tag(register)
def tweets_for_user(*args):
    return tweets_for("user_name", args)

@register_as_tag(register)
def tweets_for_list(*args):
    return tweets_for("list_name", args, per_user=1)

@register_as_tag(register)
def tweets_for_search(*args):
    return tweets_for("search_term", args)

