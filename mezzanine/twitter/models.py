
import re
from datetime import datetime, timedelta
from time import timezone
from urllib2 import urlopen, quote

from django.db import models
from django.utils.html import urlize
from django.utils.simplejson import loads
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from mezzanine.twitter.managers import TweetManager
from mezzanine.utils.timezone import make_aware
from mezzanine.twitter import (QUERY_TYPE_CHOICES, QUERY_TYPE_USER,
                               QUERY_TYPE_LIST, QUERY_TYPE_SEARCH)


re_usernames = re.compile("@([0-9a-zA-Z+_]+)", re.IGNORECASE)
re_hashtags = re.compile("#([0-9a-zA-Z+_]+)", re.IGNORECASE)
replace_hashtags = "<a href=\"http://twitter.com/search?q=%23\\1\">#\\1</a>"
replace_usernames = "<a href=\"http://twitter.com/\\1\">@\\1</a>"


class Query(models.Model):

    type = models.CharField(_("Type"), choices=QUERY_TYPE_CHOICES,
                            max_length=10)
    value = models.CharField(_("Value"), max_length=140)
    interested = models.BooleanField("Interested", default=True)

    class Meta:
        verbose_name = _("Twitter query")
        verbose_name_plural = _("Twitter queries")
        ordering = ("-id",)

    def __unicode__(self):
        return "%s: %s" % (self.get_type_display(), self.value)

    def run(self):
        """
        Request new tweets from the Twitter API.
        """
        urls = {
            QUERY_TYPE_USER: ("http://api.twitter.com/1/statuses/"
                              "user_timeline/%s.json?include_rts=true" %
                              self.value.lstrip("@")),
            QUERY_TYPE_LIST: ("http://api.twitter.com/1/%s/statuses.json"
                              "?include_rts=true" %
                              self.value.lstrip("@").replace("/", "/lists/")),
            QUERY_TYPE_SEARCH: "http://search.twitter.com/search.json?q=%s" %
                               quote(self.value.encode("utf-8")),
        }
        try:
            url = urls[self.type]
        except KeyError:
            return
        try:
            tweets = loads(urlopen(url).read())
        except:
            return
        if self.type == "search":
            tweets = tweets["results"]
        for tweet_json in tweets:
            remote_id = str(tweet_json["id"])
            tweet, created = self.tweets.get_or_create(remote_id=remote_id)
            if not created:
                continue
            if "retweeted_status" in tweet_json:
                user = tweet_json["user"]
                tweet.retweeter_user_name = user["screen_name"]
                tweet.retweeter_full_name = user["name"]
                tweet.retweeter_profile_image_url = user["profile_image_url"]
                tweet_json = tweet_json["retweeted_status"]
            if self.type == QUERY_TYPE_SEARCH:
                tweet.user_name = tweet_json["from_user"]
                tweet.full_name = tweet_json["from_user"]
                tweet.profile_image_url = tweet_json["profile_image_url"]
                date_format = "%a, %d %b %Y %H:%M:%S +0000"
            else:
                user = tweet_json["user"]
                tweet.user_name = user["screen_name"]
                tweet.full_name = user["name"]
                tweet.profile_image_url = user["profile_image_url"]
                date_format = "%a %b %d %H:%M:%S +0000 %Y"
            tweet.text = urlize(tweet_json["text"])
            tweet.text = re_usernames.sub(replace_usernames, tweet.text)
            tweet.text = re_hashtags.sub(replace_hashtags, tweet.text)
            if getattr(settings, 'TWITTER_STRIP_HIGH_MULTIBYTE', False):
                chars = [ch for ch in tweet.text if ord(ch) < 0x800]
                tweet.text = ''.join(chars)
            d = datetime.strptime(tweet_json["created_at"], date_format)
            d -= timedelta(seconds=timezone)
            tweet.created_at = make_aware(d)
            tweet.save()
        self.interested = False
        self.save()


class Tweet(models.Model):

    remote_id = models.CharField(_("Twitter ID"), max_length=50)
    created_at = models.DateTimeField(_("Date/time"), null=True)
    text = models.TextField(_("Message"), null=True)
    profile_image_url = models.URLField(_("Profile image URL"), null=True)
    user_name = models.CharField(_("User name"), max_length=100, null=True)
    full_name = models.CharField(_("Full name"), max_length=100, null=True)
    retweeter_profile_image_url = models.URLField(
        _("Profile image URL (Retweeted by)"), null=True)
    retweeter_user_name = models.CharField(
        _("User name (Retweeted by)"), max_length=100, null=True)
    retweeter_full_name = models.CharField(
        _("Full name (Retweeted by)"), max_length=100, null=True)
    query = models.ForeignKey("Query", related_name="tweets")

    objects = TweetManager()

    class Meta:
        verbose_name = _("Tweet")
        verbose_name_plural = _("Tweets")
        ordering = ("-created_at",)

    def __unicode__(self):
        return "%s: %s" % (self.user_name, self.text)

    def is_retweet(self):
        return self.retweeter_user_name is not None
