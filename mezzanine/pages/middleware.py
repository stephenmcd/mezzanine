
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.http import urlquote

from mezzanine.conf import settings
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page
from mezzanine.pages.views import page as page_view
from mezzanine.utils.urls import path_to_slug


class PageMiddleware(object):
    """
    Adds a page to the template context for the current response.

    If no page matches the URL, and the view function is not the
    fall-back page view, we try and find the page with the deepest
    URL that matches within the current URL, as in this situation,
    the app's urlpattern is considered to sit "under" a given page,
    for example the blog page will be used when individual blog
    posts are viewed. We want the page for things like breadcrumb
    nav, and page processors, but most importantly so the page's
    ``login_required`` flag can be honoured.

    If a page is matched, and the fall-back page view is called,
    we add the page to the ``extra_context`` arg of the page view,
    which it can then use to choose which template to use.

    In either case, we add the page to the response's template
    context, so that the current page is always available.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):

        slug = path_to_slug(request.path_info)
        pages = Page.objects.with_ascendants_for_slug(slug,
                        for_user=request.user, include_login_required=True)
        if pages:
            page = pages[0]
        else:
            # If we can't find a page matching this slug or any
            # of its sub-slugs, skip all further processing.
            return None

        # Handle ``page.login_required``.
        if page.login_required and not request.user.is_authenticated():
            path = urlquote(request.get_full_path())
            bits = (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
            return redirect("%s?%s=%s" % bits)

        if page.slug == slug and view_func == page_view:
            # Add the page to the ``extra_context`` arg for the
            # page view, which is responsible for choosing which
            # template to use, and raising 404 if there's no page
            # instance loaded.
            view_kwargs.setdefault("extra_context", {})
            view_kwargs["extra_context"]["page"] = page

        # Create the response, and check that we can add context
        # to it. If not, it's something like a redirect, so we
        # just return it.
        response = view_func(request, *view_args, **view_kwargs)
        if not hasattr(response, "context_data"):
            return response

        # Add the page to its template context, and set helper
        # attributes like ``is_current``.
        response.context_data["page"] = page
        try:
            response.context_data["editable_obj"]
        except KeyError:
            response.context_data["editable_obj"] = page
        response.context_data["_current_page"] = page
        page.set_helpers(response.context_data)

        # Run page processors.
        model_processors = page_processors.processors[page.content_model]
        slug_processors = page_processors.processors["slug:%s" % page.slug]
        for (processor, exact_page) in slug_processors + model_processors:
            if exact_page and not page.is_current:
                continue
            processor_response = processor(request, page)
            if isinstance(processor_response, HttpResponse):
                return processor_response
            elif processor_response:
                try:
                    response.context_data.update(processor_response)
                except (TypeError, ValueError):
                    name = "%s.%s" % (processor.__module__, processor.__name__)
                    error = ("The page processor %s returned %s but must "
                             "return HttpResponse or dict." %
                             (name, type(processor_response)))
                    raise ValueError(error)

        return response
