
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import get_model, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from mezzanine.generic.models import Keyword, Rating
from mezzanine.utils.views import set_cookie


@staff_member_required
def admin_keywords_submit(request):
    """
    Adds any new given keywords from the custom keywords field in the
    admin, and returns their IDs for use when saving a model with a
    keywords field.
    """
    ids = []
    for title in request.POST.get("text_keywords", "").split(","):
        title = "".join([c for c in title if c.isalnum() or c == "-"]).lower()
        if title:
            keyword, created = Keyword.objects.get_or_create(title=title)
            ids.append(str(keyword.id))
    return HttpResponse(",".join(set(ids)))


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
    ratings = request.COOKIES.get("mezzanine-rating", "").split(",")
    rating_string = "%s.%s" % (request.POST["content_type"],
                               request.POST["object_pk"])
    if rating_string in ratings:
        # Already rated so abort.
        return HttpResponseRedirect(url)
    obj.rating.add(Rating(value=rating_value))
    response = HttpResponseRedirect(url)
    ratings.append(rating_string)
    expiry = 60 * 60 * 24 * 365
    set_cookie(response, "mezzanine-rating", ",".join(ratings), expiry)
    return response
