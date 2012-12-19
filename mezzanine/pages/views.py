
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from mezzanine.conf import settings
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page
from mezzanine.utils.urls import home_slug
from mezzanine.utils.views import render


page_processors.autodiscover()


@staff_member_required
def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """

    def get_id(s):
        s = s.split("_")[-1]
        return s if s != "null" else None
    page = get_object_or_404(Page, id=get_id(request.POST['id']))
    old_parent_id = page.parent_id
    new_parent_id = get_id(request.POST['parent_id'])
    if new_parent_id != page.parent_id:
        # Parent changed - set the new parent and re-order the
        # previous siblings.
        page.parent_id = new_parent_id
        page.save()
        page.reset_slugs()
        pages = Page.objects.filter(parent_id=old_parent_id)
        for i, page in enumerate(pages.order_by('_order')):
            Page.objects.filter(id=page.id).update(_order=i)
    # Set the new order for the moved page and its current siblings.
    for i, page_id in enumerate(request.POST.getlist('siblings[]')):
        Page.objects.filter(id=get_id(page_id)).update(_order=i)
    return HttpResponse("ok")


def page(request, slug, template=u"pages/page.html", extra_context=None):
    """
    Select a template for a page and render it. The ``extra_context``
    arg will include a ``page`` object that's added via
    ``mezzanine.pages.middleware.PageMiddleware``. The page is loaded
    via the middleware so that other apps with urlpatterns that match
    the current page can include a page in their template context.
    The urlpattern that maps to this view is a catch-all pattern, in
    which case the page instance will be None, so raise a 404 then.

    For template selection, a list of possible templates is built up
    based on the current page. This list is order from most granular
    match, starting with a custom template for the exact page, then
    adding templates based on the page's parent page, that could be
    used for sections of a site (eg all children of the parent).
    Finally at the broadest level, a template for the page's content
    type (it's model class) is checked for, and then if none of these
    templates match, the default pages/page.html is used.
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
    template_name = unicode(slug) if slug != home_slug() else "index"
    templates = [u"pages/%s.html" % template_name]
    if page.content_model is not None:
        templates.append(u"pages/%s/%s.html" % (template_name,
            page.content_model))
    for parent in page.get_ascendants():
        parent_template_name = unicode(parent.slug)
        # Check for a template matching the page's content model.
        if page.content_model is not None:
            templates.append(u"pages/%s/%s.html" % (parent_template_name,
                page.content_model))
    # Check for a template matching the page's content model.
    if page.content_model is not None:
        templates.append(u"pages/%s.html" % page.content_model)
    templates.append(template)
    return render(request, templates, extra_context)
