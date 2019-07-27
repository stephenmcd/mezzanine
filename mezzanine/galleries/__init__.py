"""
Implements a photo gallery content type.
"""
from __future__ import unicode_literals

from mezzanine import __version__  # noqa
from mezzanine.utils.models import get_swappable_model


def get_gallery_model():
    return get_swappable_model("GALLERY_MODEL")


def get_gallery_image_model():
    return get_swappable_model("GALLERY_IMAGE_MODEL")
