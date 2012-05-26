from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.http import urlquote

from mezzanine.conf import settings
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page
from mezzanine.pages.views import page as page_view


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

        slug = request.path
        if slug != "/":
            slug = slug.strip("/")
        pages_for_user = Page.objects.published(request.user)
        try:
            page = pages_for_user.get(slug=slug)
        except Page.DoesNotExist:
            page = None
            if view_func != page_view:
                # A non-page urlpattern has been matched with no page.
                # To find the page this is under, we work out way right
                # from the left of the URL, and bail out as soon as we
                # don't match a page, keeping the last one found.
                slug = slug.split("/")
                for i, part in enumerate(slug):
                    try:
                        page = pages_for_user.get(slug="/".join(slug[:i + 1]))
                    except Page.DoesNotExist:
                        break
        else:
            if view_func == page_view:
                # Add the page to the ``extra_context`` arg for the
                # page view, which is responsible for choosing which
                # template to use, and raising 404 if there's no page
                # instance loaded.
                view_kwargs.setdefault("extra_context", {})
                view_kwargs["extra_context"]["page"] = page

        # Create the response, and add the page to its template
        # context. Response could also be a redirect, which we catch
        # rather than checking for each type of response.
        response = view_func(request, *view_args, **view_kwargs)
        try:
            response.context_data["page"] = page
        except AttributeError:
            pass

        # If we don't have a page, bail out, since no more handling
        # is required.
        if page is None:
            return response

        # Handle ``page.login_required``.
        if page.login_required and not request.user.is_authenticated():
            path = urlquote(request.get_full_path())
            bits = (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
            return redirect("%s?%s=%s" % bits)

        # If we don't have a response that we can add context to,
        # eg a redirect, just return it.
        if not hasattr(response, "context_data"):
            return response

        # Run page processors.
        model_processors = page_processors.processors[page.content_model]
        slug_processors = page_processors.processors["slug:%s" % page.slug]
        for processor in model_processors + slug_processors:
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
