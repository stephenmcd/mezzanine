"""
Provides models and utilities for displaying different types of Twitter feeds.
"""

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
