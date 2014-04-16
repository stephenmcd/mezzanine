"""
Provides models and utilities for displaying different types of Twitter feeds.
"""
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mezzanine import __version__


# Constants/choices for the different query types.

QUERY_TYPE_USER = "user"
QUERY_TYPE_LIST = "list"
QUERY_TYPE_SEARCH = "search"
QUERY_TYPE_CHOICES = (
    (QUERY_TYPE_USER, _("User")),
    (QUERY_TYPE_LIST, _("List")),
    (QUERY_TYPE_SEARCH, _("Search")),
)


def get_auth_settings():
    """
    Returns all the key/secret settings for Twitter access,
    only if they're all defined.
    """
    from mezzanine.conf import settings
    settings.use_editable()
    auth_settings = (settings.TWITTER_CONSUMER_KEY,
                     settings.TWITTER_CONSUMER_SECRET,
                     settings.TWITTER_ACCESS_TOKEN_KEY,
                     settings.TWITTER_ACCESS_TOKEN_SECRET)
    return auth_settings if all(auth_settings) else None
