"""
A port of django-forms-builder for Mezzanine. Allows admin users to create
their own HTML5 forms and export form submissions as CSV.
"""
from __future__ import unicode_literals

from mezzanine import __version__  # noqa
from mezzanine.utils.models import get_swappable_model


def get_form_model():
    return get_swappable_model("FORM_MODEL")


def get_field_model():
    return get_swappable_model("FIELD_MODEL")


def get_form_entry_model():
    return get_swappable_model("FORM_ENTRY_MODEL")


def get_field_entry_model():
    return get_swappable_model("FIELD_ENTRY_MODEL")
