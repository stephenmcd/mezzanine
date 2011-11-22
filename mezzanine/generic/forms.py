
from django import forms
from django.contrib.comments.forms import CommentSecurityForm, CommentForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from mezzanine.generic.models import Keyword, ThreadedComment, RATING_RANGE
from mezzanine.utils.urls import content_media_urls


class KeywordsWidget(forms.MultiWidget):
    """
    Form field for the ``KeywordsField`` generic relation field. Since
    the admin with model forms has no form field for generic
    relations, this form field provides a single field for managing
    the keywords. It contains two actual widgets, a text input for
    entering keywords, and a hidden input that stores the ID of each
    ``Keyword`` instance.

    The attached JavaScript adds behaviour so that when the form is
    submitted, an AJAX post is made that passes the list of keywords
    in the text input, and returns a list of keyword IDs which are
    then entered into the hidden input before the form submits. The
    list of IDs in the hidden input is what is used when retrieving
    an actual value from the field for the form.
    """

    class Media:
        js = content_media_urls("js/jquery-1.4.4.min.js",
                                "js/keywords_field.js")

    def __init__(self, attrs=None):
        """
        Setup the text and hidden form field widgets.
        """
        widgets = (forms.HiddenInput,
                   forms.TextInput(attrs={"class": "vTextField"}))
        super(KeywordsWidget, self).__init__(widgets, attrs)
        self._ids = []

    def decompress(self, value):
        """
        Takes the sequence of ``AssignedKeyword`` instances and splits
        them into lists of keyword IDs and titles each mapping to one
        of the form field widgets.
        """
        if hasattr(value, "select_related"):
            keywords = [a.keyword for a in value.select_related("keyword")]
            if keywords:
                keywords = [(str(k.id), k.title) for k in keywords]
                self._ids, words = zip(*keywords)
                return (",".join(self._ids), ", ".join(words))
        return ("", "")

    def format_output(self, rendered_widgets):
        """
        Wraps the output HTML with a list of all available ``Keyword``
        instances that can be clicked on to toggle a keyword.
        """
        rendered = super(KeywordsWidget, self).format_output(rendered_widgets)
        links = ""
        for keyword in Keyword.objects.all().order_by("title"):
            prefix = "+" if str(keyword.id) not in self._ids else "-"
            links += ("<a href='#'>%s%s</a>" % (prefix, unicode(keyword)))
        rendered += mark_safe("<p class='keywords-field'>%s</p>" % links)
        return rendered

    def value_from_datadict(self, data, files, name):
        """
        Return the comma separated list of keyword IDs for use in
        ``KeywordsField.save_form_data()``.
        """
        return data.get("%s_0" % name, "")


class ThreadedCommentForm(CommentForm):

    name = forms.CharField(label=_("Name"), help_text=_("required"),
                           max_length=50)
    email = forms.EmailField(label=_("Email"),
                             help_text=_("required (not published)"))
    url = forms.URLField(label=_("Website"), help_text=_("optional"),
                         required=False)

    def get_comment_model(self):
        """
        Use the custom comment model instead of the built-in one.
        """
        return ThreadedComment


class RatingForm(CommentSecurityForm):
    """
    Form for a rating. Subclasses ``CommentSecurityForm`` to make use
    of its easy setup for generic relations.
    """
    value = forms.ChoiceField(label=_("Rating"), widget=forms.RadioSelect,
                              choices=zip(RATING_RANGE, RATING_RANGE))
