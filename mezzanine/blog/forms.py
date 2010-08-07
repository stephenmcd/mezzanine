
from django import forms

from mezzanine.blog.models import Comment, BlogPost


class CommentForm(forms.ModelForm):
    """
    Model form for ``Comment`` against a ``BlogPost``.
    """

    class Meta:
        model = Comment
        fields = ("name", "email", "website", "body",)


class BlogPostForm(forms.ModelForm):
    """
    Model form for ``BlogPost`` that provides the quick blog panel in the
    admin dashboard.
    """

    class Meta:
        model = BlogPost
        fields = ("title", "content", "status")

    def __init__(self):
        super(BlogPostForm, self).__init__()
        self.fields["status"].widget = forms.HiddenInput()
