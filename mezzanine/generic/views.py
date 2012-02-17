
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import get_model, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from mezzanine.generic.forms import ThreadedCommentForm
from mezzanine.generic.models import Keyword, Rating
from mezzanine.utils.views import render, set_cookie


@staff_member_required
def admin_keywords_submit(request):
    """
    Adds any new given keywords from the custom keywords field in the
    admin, and returns their IDs for use when saving a model with a
    keywords field.
    """
    ids, titles = [], []
    for title in request.POST.get("text_keywords", "").split(","):
        title = "".join([c for c in title if c.isalnum() or c in "- "])
        title = title.strip().lower()
        if title:
            keyword, created = Keyword.objects.get_or_create(title=title)
            id = str(keyword.id)
            if id not in ids:
                ids.append(id)
                titles.append(title)
    return HttpResponse("%s|%s" % (",".join(ids), ", ".join(titles)))


def comment(request, template="generic/comments.html"):
    """
    Handle a ``ThreadedCommentForm`` submission and redirect back to its
    related object.
    """
    try:
        model = get_model(*request.POST["content_type"].split(".", 1))
        obj = model.objects.get(id=request.POST["object_pk"])
        if request.method != "POST":
            raise ObjectDoesNotExist()
    except (KeyError, TypeError, AttributeError, ObjectDoesNotExist):
        # Something was missing from the post so abort.
        return HttpResponseRedirect("/")
    form = ThreadedCommentForm(request, obj, request.POST or None)
    if form.is_valid():
        comment = form.get_comment_object()
        if request.user.is_authenticated():
            comment.user = request.user
        comment.by_author = request.user == getattr(obj, "user", None)
        comment.ip_address = request.META.get("HTTP_X_FORWARDED_FOR",
                                              request.META["REMOTE_ADDR"])
        comment.replied_to_id = request.POST.get("replied_to")
        comment.save()
        response = HttpResponseRedirect(comment.get_absolute_url())
        # Store commenter's details in a cookie for 90 days.
        cookie_expires = 60 * 60 * 24 * 90
        for field in ThreadedCommentForm.cookie_fields:
            cookie_name = ThreadedCommentForm.cookie_prefix + field
            cookie_value = request.POST.get(field, "")
            set_cookie(response, cookie_name, cookie_value, cookie_expires)
        return response
    else:
        # Show errors with stand-alone comment form.
        context = {"obj": obj, "posted_comment_form": form}
        return render(request, template, context)


def rating(request):
    """
    Handle a ``RatingForm`` submission and redirect back to its
    related object.
    """
    try:
        model = get_model(*request.POST["content_type"].split(".", 1))
        obj = model.objects.get(id=request.POST["object_pk"])
        url = obj.get_absolute_url() + "#rating-%s" % obj.id
        field = getattr(obj, request.POST["field_name"])
        if field.model != Rating:
            raise TypeError("Not a rating field.")
    except (KeyError, TypeError, AttributeError, ObjectDoesNotExist):
        # Something was missing from the post so abort.
        return HttpResponseRedirect("/")
    try:
        rating_value = int(request.POST["value"])
    except (KeyError, ValueError):
        return HttpResponseRedirect(url)
    rated = request.COOKIES.get("mezzanine-rating", "").split(",")
    cookie = "%(content_type)s.%(object_pk)s.%(field_name)s" % request.POST
    if cookie in rated:
        # Already rated so abort.
        return HttpResponseRedirect(url)
    field.add(Rating(value=rating_value))
    response = HttpResponseRedirect(url)
    rated.append(cookie)
    expiry = 60 * 60 * 24 * 365
    set_cookie(response, "mezzanine-rating", ",".join(rated), expiry)
    return response
