
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, Http404

from mezzanine.conf import settings
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page
from mezzanine.utils.views import render


page_processors.autodiscover()


def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """
    get_id = lambda s: s.split("_")[-1]
    for ordering in ("ordering_from", "ordering_to"):
        ordering = request.POST.get(ordering, "")
        if ordering:
            for i, page in enumerate(ordering.split(",")):
                try:
                    Page.objects.filter(id=get_id(page)).update(_order=i)
                except Exception, e:
                    return HttpResponse(str(e))
    try:
        moved_page = int(get_id(request.POST.get("moved_page", "")))
    except ValueError, e:
        pass
    else:
        moved_parent = get_id(request.POST.get("moved_parent", ""))
        if not moved_parent:
            moved_parent = None
        try:
            page = Page.objects.get(id=moved_page)
            page.parent_id = moved_parent
            page.save()
            page.reset_slugs()
        except Exception, e:
            return HttpResponse(str(e))
    return HttpResponse("ok")
admin_page_ordering = staff_member_required(admin_page_ordering)


def page(request, slug, template="pages/page.html", extra_context=None):
    """
    Select a template for a page and render it. The ``extra_context``
    arg will include a ``page`` object that's added via
    ``mezzanine.pages.middleware.PageMiddleware``. The page is loaded
    via the middleware so that other apps with urlpatterns that match
    the current page can include a page in their template context.
    The urlpattern that maps to this view is a catch-all pattern, in
    which case the page instance will be None, so raise a 404 then.
    """
    page_middleware = "mezzanine.pages.middleware.PageMiddleware"
    if page_middleware not in settings.MIDDLEWARE_CLASSES:
        raise ImproperlyConfigured(page_middleware + " is missing from " +
                                   "settings.MIDDLEWARE_CLASSES")

    extra_context = extra_context or {}
    try:
        page = extra_context["page"]
    except KeyError:
        raise Http404
    # Check for a template name matching the page's slug. If the homepage
    # is configured as a page instance, the template "pages/index.html" is
    # used, since the slug "/" won't match a template name.
    template_name = unicode(slug) if slug != "/" else "index"
    templates = [u"pages/%s.html" % template_name]
    # Check for a template matching the page's content model.
    if page.content_model is not None:
        templates.append(u"pages/%s.html" % page.content_model)
    templates.append(template)
    return render(request, templates, extra_context)
