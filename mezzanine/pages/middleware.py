from __future__ import unicode_literals

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse, Http404

from mezzanine.conf import settings
from mezzanine.pages import context_processors, page_processors
from mezzanine.pages.models import Page
from mezzanine.pages.views import page as page_view
from mezzanine.utils.deprecation import MiddlewareMixin, get_middleware_setting
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.urls import path_to_slug


class PageMiddleware(MiddlewareMixin):
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

    def __init__(self, *args, **kwargs):
        super(PageMiddleware, self).__init__(*args, **kwargs)
        if "mezzanine.pages" not in settings.INSTALLED_APPS:
            raise MiddlewareNotUsed

    @classmethod
    def installed(cls):
        """
        Used in ``mezzanine.pages.views.page`` to ensure
        ``PageMiddleware`` or a subclass has been installed. We cache
        the result on the ``PageMiddleware._installed`` to only run
        this once. Short path is to just check for the dotted path to
        ``PageMiddleware`` in ``MIDDLEWARE_CLASSES`` - if not found,
        we need to load each middleware class to match a subclass.
        """
        try:
            return cls._installed
        except AttributeError:
            name = "mezzanine.pages.middleware.PageMiddleware"
            mw_setting = get_middleware_setting()
            installed = name in mw_setting
            if not installed:
                for name in mw_setting:
                    if issubclass(import_dotted_path(name), cls):
                        installed = True
                        break
            setattr(cls, "_installed", installed)
            return installed

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Per-request mechanics for the current page object.
        """

        # Load the closest matching page by slug, and assign it to the
        # request object. If none found, skip all further processing.
        slug = path_to_slug(request.path_info)
        pages = Page.objects.with_ascendants_for_slug(slug,
                        for_user=request.user, include_login_required=True)
        if pages:
            page = pages[0]
            setattr(request, "page", page)
            context_processors.page(request)
        else:
            return

        # Handle ``page.login_required``.
        if page.login_required and not request.user.is_authenticated():
            return redirect_to_login(request.get_full_path())

        # If the view isn't Mezzanine's page view, try to return the result
        # immediately. In the case of a 404 with an URL slug that matches a
        # page exactly, swallow the exception and try Mezzanine's page view.
        #
        # This allows us to set up pages with URLs that also match non-page
        # urlpatterns. For example, a page could be created with the URL
        # /blog/about/, which would match the blog urlpattern, and assuming
        # there wasn't a blog post with the slug "about", would raise a 404
        # and subsequently be rendered by Mezzanine's page view.
        if view_func != page_view:
            try:
                return view_func(request, *view_args, **view_kwargs)
            except Http404:
                if page.slug != slug:
                    raise

        # Run page processors.
        extra_context = {}
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
                    for k, v in processor_response.items():
                        if k not in extra_context:
                            extra_context[k] = v
                except (TypeError, ValueError):
                    name = "%s.%s" % (processor.__module__, processor.__name__)
                    error = ("The page processor %s returned %s but must "
                             "return HttpResponse or dict." %
                             (name, type(processor_response)))
                    raise ValueError(error)

        return page_view(request, slug, extra_context=extra_context)
