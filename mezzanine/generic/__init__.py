"""
Provides various models and associated functionality, that can be 
related to any other model using generic relationshipswith Django's 
contenttypes framework, such as comments, keywords/tags and voting.
"""

from mezzanine.generic.models import ThreadedComment
from mezzanine.generic.forms import ThreadedCommentForm

# These methods are part of the API for django.contrib.comments

def get_model():
    return ThreadedComment

def get_form():
    return ThreadedCommentForm
