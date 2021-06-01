import re
from datetime import datetime
from urllib.parse import quote

import requests
from django.db import models
from django.utils.html import urlize
from django.utils.timezone import make_aware, utc
from django.utils.translation import gettext_lazy as _
from requests_oauthlib import OAuth1

from mezzanine.conf import settings
from mezzanine.twitter import (
    QUERY_TYPE_CHOICES,
    QUERY_TYPE_LIST,
    QUERY_TYPE_SEARCH,
    QUERY_TYPE_USER,
    get_auth_settings,
)
from mezzanine.twitter.managers import TweetManager

re_usernames = re.compile(r"(^|\W)@([0-9a-zA-Z+_]+)", re.IGNORECASE)
re_hashtags = re.compile(r"#([0-9a-zA-Z+_]+)", re.IGNORECASE)
replace_hashtags = '<a href="http://twitter.com/search?q=%23\\1">#\\1</a>'
replace_usernames = '\\1<a href="http://twitter.com/\\2">@\\2</a>'


class TwitterQueryException(Exception):
    pass


class Query(models.Model):

    type = models.CharField(_("Type"), choices=QUERY_TYPE_CHOICES, max_length=10)
    value = models.CharField(_("Value"), max_length=140)
    interested = models.BooleanField("Interested", default=True)

    class Meta:
        verbose_name = _("Twitter query")
        verbose_name_plural = _("Twitter queries")
        ordering = ("-id",)

    def __str__(self):
        return f"{self.get_type_display()}: {self.value}"

    def run(self):
        """
        Request new tweets from the Twitter API.
        """
        try:
            value = quote(self.value)
        except KeyError:
            value = self.value
        urls = {
            QUERY_TYPE_USER: (
                "https://api.twitter.com/1.1/statuses/"
                "user_timeline.json?screen_name=%s"
                "&include_rts=true" % value.lstrip("@")
            ),
            QUERY_TYPE_LIST: (
                "https://api.twitter.com/1.1/lists/statuses.json"
                "?list_id=%s&include_rts=true" % value
            ),
            QUERY_TYPE_SEARCH: "https://api.twitter.com/1.1/search/tweets.json"
            "?q=%s" % value,
        }
        try:
            url = urls[self.type]
        except KeyError:
            raise TwitterQueryException("Invalid query type: %s" % self.type)
        auth_settings = get_auth_settings()
        if not auth_settings:
            from mezzanine.conf import registry

            if self.value == registry["TWITTER_DEFAULT_QUERY"]["default"]:
                # These are some read-only keys and secrets we use
                # for the default query (eg nothing has been configured)
                auth_settings = (
                    "KxZTRD3OBft4PP0iQW0aNQ",
                    "sXpQRSDUVJ2AVPZTfh6MrJjHfOGcdK4wRb1WTGQ",
                    "1368725588-ldWCsd54AJpG2xcB5nyTHyCeIC3RJcNVUAkB1OI",
                    "r9u7qS18t8ad4Hu9XVqmCGxlIpzoCN3e1vx6LOSVgyw3R",
                )
            else:
                raise TwitterQueryException("Twitter OAuth settings missing")
        try:
            tweets = requests.get(url, auth=OAuth1(*auth_settings)).json()
        except Exception as e:
            raise TwitterQueryException("Error retrieving: %s" % e)
        try:
            raise TwitterQueryException(tweets["errors"][0]["message"])
        except (IndexError, KeyError, TypeError):
            pass
        if self.type == "search":
            tweets = tweets["statuses"]
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
                tweet.user_name = tweet_json["user"]["screen_name"]
                tweet.full_name = tweet_json["user"]["name"]
                tweet.profile_image_url = tweet_json["user"]["profile_image_url"]
                date_format = "%a %b %d %H:%M:%S +0000 %Y"
            else:
                user = tweet_json["user"]
                tweet.user_name = user["screen_name"]
                tweet.full_name = user["name"]
                tweet.profile_image_url = user["profile_image_url"]
                date_format = "%a %b %d %H:%M:%S +0000 %Y"
            tweet.text = urlize(tweet_json["text"])
            tweet.text = re_usernames.sub(replace_usernames, tweet.text)
            tweet.text = re_hashtags.sub(replace_hashtags, tweet.text)
            if getattr(settings, "TWITTER_STRIP_HIGH_MULTIBYTE", False):
                chars = [ch for ch in tweet.text if ord(ch) < 0x800]
                tweet.text = "".join(chars)
            d = datetime.strptime(tweet_json["created_at"], date_format)
            tweet.created_at = make_aware(d, utc)
            try:
                tweet.save()
            except Warning:
                pass
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
        _("Profile image URL (Retweeted by)"), null=True
    )
    retweeter_user_name = models.CharField(
        _("User name (Retweeted by)"), max_length=100, null=True
    )
    retweeter_full_name = models.CharField(
        _("Full name (Retweeted by)"), max_length=100, null=True
    )
    query = models.ForeignKey("Query", on_delete=models.CASCADE, related_name="tweets")

    objects = TweetManager()

    class Meta:
        verbose_name = _("Tweet")
        verbose_name_plural = _("Tweets")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user_name}: {self.text}"

    def is_retweet(self):
        return self.retweeter_user_name is not None
