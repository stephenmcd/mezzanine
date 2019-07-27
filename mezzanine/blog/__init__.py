"""
Provides a blogging app with posts, keywords, categories and comments.
Posts can be listed by month, keyword, category or author.
"""
from __future__ import unicode_literals

from mezzanine import __version__  # noqa
from mezzanine.utils.models import get_swappable_model


def get_post_model():
    return get_swappable_model("BLOG_POST_MODEL")


def get_category_model():
    return get_swappable_model("BLOG_CATEGORY_MODEL")
