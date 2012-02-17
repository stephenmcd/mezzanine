
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import get_model, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from mezzanine.generic.fields import RatingField
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
    except (KeyError, TypeError, AttributeError, ObjectDoesNotExist):
        # Something was missing from the post so abort.
        return HttpResponseRedirect("/")
    try:
        rating_value = int(request.POST["value"])
    except (KeyError, ValueError):
        return HttpResponseRedirect(url)
    # There can only be one ``RatingField``, find its manager.
    for field in obj._meta.many_to_many:
        if isinstance(field, RatingField):
            rating_manager = getattr(obj, field.name)
            break
    else:
        raise TypeError("%s doesn't contain a RatingField." % obj)
    ratings = request.COOKIES.get("mezzanine-rating", "").split(",")
    rating_string = "%s.%s" % (request.POST["content_type"],
                               request.POST["object_pk"])
    if rating_string in ratings:
        # Already rated so abort.
        return HttpResponseRedirect(url)
    rating_manager.add(Rating(value=rating_value))
    response = HttpResponseRedirect(url)
    ratings.append(rating_string)
    expiry = 60 * 60 * 24 * 365
    set_cookie(response, "mezzanine-rating", ",".join(ratings), expiry)
    return response
