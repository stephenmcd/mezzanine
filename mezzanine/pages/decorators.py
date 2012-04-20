
from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.utils.http import urlquote

from mezzanine.conf import settings
from mezzanine.pages.models import Page


def for_page(slug):
    """
    Decorator for views that have a urlpattern matching a page in
    Mezzanine's navigation tree.
    """
    slug = slug or "/"

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                page = Page.objects.published(request.user).get(slug=slug)
            except Page.DoesNotExist:
                page = None
            else:
                if page.login_required and not request.user.is_authenticated():
                    path = urlquote(request.get_full_path())
                    url = "%s?%s=%s" % (settings.LOGIN_URL,
                                        REDIRECT_FIELD_NAME, path)
                    return redirect(url)
            response = view_func(request, *args, **kwargs)
            response.context_data["page"] = page
            return response
        return wrapper
    return decorator
