"""
Provides the main structure of a Mezzanine site with a hierarchical tree
of pages, each subclassing the Page model to create a content structure.
"""
from mezzanine import __version__  # noqa

default_app_config = "mezzanine.pages.apps.PagesConfig"
