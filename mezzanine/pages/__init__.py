"""
Provides the main structure of a Mezzanine site with a hierarchical tree
of pages, each subclassing the Page model to create a content structure.
"""
from __future__ import unicode_literals

from mezzanine import __version__  # noqa
from mezzanine.utils.models import get_swappable_model


default_app_config = 'mezzanine.pages.apps.PagesConfig'


def get_page_model():
    return get_swappable_model("PAGE_MODEL")


def get_rich_text_page_model():
    return get_swappable_model("RICH_TEXT_PAGE_MODEL")


def get_link_model():
    return get_swappable_model("LINK_MODEL")
