
from django import forms
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _

from mezzanine.generic.models import ThreadedComment


class ThreadedCommentForm(CommentForm):

    name = forms.CharField(label=_("Name"), help_text=_("required"),
                           max_length=50)
    email = forms.EmailField(label=_("Email"), 
                             help_text=_("required (not published)"))
    url = forms.URLField(label=_("Website"), help_text=_("optional"), 
                         required=False)

    def get_comment_model(self):
        """
        Use our custom comment model instead of the built-in one.
        """
        return ThreadedComment
