
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


@register.filter
def tweet_timesince(d, now=None):
    """
    Provides a timesince filter that matches Twitter's
    """
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    # If now not supplied, make it now
    if not now:
        if d.tzinfo:
            now = datetime.datetime.now(LocalTimezone(d))
        else:
            now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds

    ago = ugettext('ago')
    # If it's in the future, output "0 seconds ago"
    if since < 0:
        s = u'0 ' + ugettext('seconds') + ' ' + ago
    # If it's been a day or more, output the date in the format "dd mmm" (01 Oct)
    if since >= 86400:
        # Not likely with Twitter, but in case we get a year < 1900
        s = ugettext(datetime.date(2010, d.month, d.day).strftime("%d %b"))
    # If it's not been a day, but more than an hour, output hours (3 hours ago)
    elif since >= 3600:
        n = math.floor(since / 3600.0)
        s = '%d ' % n + ' ' + ungettext('hour', 'hours', n) + ' ' + ago
    # If it's not be an hour, but more than a minute, output minutes (7 minutes ago)
    elif since >= 60:
        n = math.floor(since / 60.0)
        s = '%d ' %  + ' ' + ungettext('minute', 'minutes', n) + ' ' + ago
    # If it's not been a minute, but more than 0 seconds
    else:
        s = '%d ' % since + ungettext('second', 'seconds', n) + ' ' + ago

    return s

