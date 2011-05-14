
from django.http import HttpResponseRedirect

from mezzanine.generic.forms import ThreadedCommentForm
from mezzanine.utils.views import set_cookie


def handle_comments(obj, request):
    """
    A problem exists with having a single URL to handle posting
    generic data. If there's an error with the form, we have to either
    display the form with errors on a different page than the page
    where the form was originally rendered, or redirect back to the
    original page and lose the form errors.

    This function can be called from any view that contains comments.
    It returns a 3-item sequence containing two forms, one with posted
    data and one without, which are each used to build the threaded
    comment tree with forms for replying. The third item returned is
    a response object to redirect to if a comment is successfully
    posted.
    """

    # Create two comment forms - one with posted data and errors that will be
    # matched to the form submitted via comment_id, and an empty one for all
    # other instances.
    cookie_prefix = "mezzanine-comment-"
    cookie_fields = ("user_name", "user_email", "user_url")
    initial = {}
    for field in cookie_fields:
        initial[field] = request.COOKIES.get(cookie_prefix + field, "")
    posted = request.POST or None
    posted_comment_form = ThreadedCommentForm(obj, posted, initial=initial)
    unposted_comment_form = ThreadedCommentForm(obj, initial=initial)
    response = None
    if request.method == "POST" and posted_comment_form.is_valid():
        comment = posted_comment_form.get_comment_object()
        comment.by_author = request.user == getattr(obj, "user", None)
        comment.ip_address = request.META.get("HTTP_X_FORWARDED_FOR",
                                              request.META["REMOTE_ADDR"])
        comment.replied_to_id = request.POST.get("replied_to")
        comment.save()
        response = HttpResponseRedirect(comment.get_absolute_url())
        # Store commenter's details in a cookie for 90 days.
        cookie_expires = 60 * 60 * 24 * 90
        for field in cookie_fields:
            cookie_name = cookie_prefix + field
            cookie_value = request.POST.get(field, "")
            set_cookie(response, cookie_name, cookie_value, cookie_expires)
    return posted_comment_form, unposted_comment_form, response
