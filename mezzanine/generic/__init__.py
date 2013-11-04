"""
Provides various models and associated functionality, that can be
related to any other model using generic relationshipswith Django's
contenttypes framework, such as comments, keywords/tags and voting.
"""
from __future__ import unicode_literals

# These methods are part of the API for django.contrib.comments


def get_model():
    from mezzanine.generic.models import ThreadedComment
    return ThreadedComment


def get_form():
    from mezzanine.generic.forms import ThreadedCommentForm
    return ThreadedCommentForm
