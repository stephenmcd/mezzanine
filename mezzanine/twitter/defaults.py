"""
Default settings for the ``mezzanine.twitter`` app. Each of these can be
overridden in your project's settings module, just like regular
Django settings. The ``editable`` argument for each controls whether
the setting is editable via Django's admin.

Thought should be given to how a setting is actually used before
making it editable, as it may be inappropriate - for example settings
that are only read during startup shouldn't be editable, since changing
them would require an application reload.
"""

from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting
from mezzanine.twitter import QUERY_TYPE_CHOICES, QUERY_TYPE_SEARCH


register_setting(
    name="TWITTER_DEFAULT_QUERY_TYPE",
    label=_("Default Twitter Query Type"),
    description=_("Type of query that will be used to retrieve tweets for "
        "the default Twitter feed."),
    editable=True,
    default=QUERY_TYPE_SEARCH,
    choices=QUERY_TYPE_CHOICES,
)

register_setting(
    name="TWITTER_DEFAULT_QUERY",
    label=_("Default Twitter Query"),
    description=_("Twitter query to use for the default query type."),
    editable=True,
    default="#django",
)

register_setting(
    name="TWITTER_DEFAULT_NUM_TWEETS",
    label=_("Default Number of Tweets"),
    description=_("Number of tweets to display in the default Twitter feed."),
    editable=True,
    default=3,
)
