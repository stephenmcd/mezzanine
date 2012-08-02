
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.messages import error
from django.contrib.comments.signals import comment_was_posted
from django.core.urlresolvers import reverse
from django.db.models import get_model, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.generic.fields import RatingField
from mezzanine.generic.forms import ThreadedCommentForm
from mezzanine.generic.models import Keyword, Rating
from mezzanine.utils.cache import add_cache_bypass
from mezzanine.utils.email import send_mail_template
from mezzanine.utils.views import render, set_cookie, is_spam


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

    post_data = request.POST
    settings.use_editable()
    if settings.COMMENTS_ACCOUNT_REQUIRED:
        if not request.user.is_authenticated():
            # Account required but user isn't authenticated - store
            # their post data in the session and redirect to login.
            request.session["unauthenticated_comment"] = post_data
            error(request, _("You must log in to comment. Please log in or "
                             "sign up, and your comment will be posted."))
            url = "%s?next=%s" % (settings.LOGIN_URL, reverse("comment"))
            return redirect(url)
        elif "unauthenticated_comment" in request.session:
            # User has logged in after post data being stored in the
            # session for an unauthenticated comment post, so use it.
            post_data = request.session.pop("unauthenticated_comment")

    try:
        model = get_model(*post_data["content_type"].split(".", 1))
        obj = model.objects.get(id=post_data["object_pk"])
    except (KeyError, TypeError, AttributeError, ObjectDoesNotExist):
        # Something was missing from the post so abort.
        return HttpResponseRedirect("/")

    form = ThreadedCommentForm(request, obj, post_data)
    if form.is_valid():
        url = obj.get_absolute_url()
        if is_spam(request, form, url):
            return redirect(url)
        comment = form.get_comment_object()
        if request.user.is_authenticated():
            comment.user = request.user
        comment.by_author = request.user == getattr(obj, "user", None)
        comment.ip_address = request.META.get("HTTP_X_FORWARDED_FOR",
                                              request.META["REMOTE_ADDR"])
        comment.replied_to_id = post_data.get("replied_to")
        comment.save()
        comment_was_posted.send(sender=comment.__class__, comment=comment,
                                request=request)
        # Send notification emails.
        comment_url = add_cache_bypass(comment.get_absolute_url())
        notify_emails = filter(None, [addr.strip() for addr in
                            settings.COMMENTS_NOTIFICATION_EMAILS.split(",")])
        if notify_emails:
            subject = _("New comment for: ") + unicode(obj)
            context = {
                "comment": comment,
                "comment_url": comment_url,
                "request": request,
                "obj": obj,
            }
            send_mail_template(subject, "email/comment_notification",
                               settings.DEFAULT_FROM_EMAIL, notify_emails,
                               context, fail_silently=settings.DEBUG)

        response = HttpResponseRedirect(comment_url)
        # Store commenter's details in a cookie for 90 days.
        cookie_expires = 60 * 60 * 24 * 90
        for field in ThreadedCommentForm.cookie_fields:
            cookie_name = ThreadedCommentForm.cookie_prefix + field
            cookie_value = post_data.get(field, "")
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
        url = add_cache_bypass(obj.get_absolute_url()) + "#rating-%s" % obj.id
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
        if request.is_ajax():
            response = HttpResponse("err")
        else:
            response = HttpResponseRedirect(url)
        return response
    rating_manager.add(Rating(value=rating_value))
    if request.is_ajax():
        # Reload the object and return the new rating.
        obj = model.objects.get(id=request.POST["object_pk"])
        response = HttpResponse(str(obj.rating_average))
    else:
        response = HttpResponseRedirect(url)
    ratings.append(rating_string)
    expiry = 60 * 60 * 24 * 365
    set_cookie(response, "mezzanine-rating", ",".join(ratings), expiry)
    return response
