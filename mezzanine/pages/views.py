from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from mezzanine.pages.models import Page, PageMoveException
from mezzanine.utils.urls import home_slug


@staff_member_required
def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """

    def get_id(s):
        s = s.split("_")[-1]
        return int(s) if s.isdigit() else None

    page = get_object_or_404(Page, id=get_id(request.POST["id"]))
    old_parent_id = page.parent_id
    new_parent_id = get_id(request.POST["parent_id"])
    new_parent = Page.objects.get(id=new_parent_id) if new_parent_id else None

    try:
        page.get_content_model().can_move(request, new_parent)
    except PageMoveException as e:
        messages.error(request, e)
        return HttpResponse("error")

    # Perform the page move
    if new_parent_id != page.parent_id:
        # Parent changed - set the new parent and re-order the
        # previous siblings.
        page.set_parent(new_parent)
        pages = Page.objects.filter(parent_id=old_parent_id)
        for i, page in enumerate(pages.order_by("_order")):
            Page.objects.filter(id=page.id).update(_order=i)
    # Set the new order for the moved page and its current siblings.
    for i, page_id in enumerate(request.POST.getlist("siblings[]")):
        Page.objects.filter(id=get_id(page_id)).update(_order=i)

    return HttpResponse("ok")


def page(request, slug, template="pages/page.html", extra_context=None):
    """
    Select a template for a page and render it. The request
    object should have a ``page`` attribute that's added via
    ``mezzanine.pages.middleware.PageMiddleware``. The page is loaded
    earlier via middleware to perform various other functions.
    The urlpattern that maps to this view is a catch-all pattern, in
    which case the page attribute won't exist, so raise a 404 then.

    For template selection, a list of possible templates is built up
    based on the current page. This list is order from most granular
    match, starting with a custom template for the exact page, then
    adding templates based on the page's parent page, that could be
    used for sections of a site (eg all children of the parent).
    Finally at the broadest level, a template for the page's content
    type (it's model class) is checked for, and then if none of these
    templates match, the default pages/page.html is used.
    """

    from mezzanine.pages.middleware import PageMiddleware

    if not PageMiddleware.installed():
        raise ImproperlyConfigured(
            "mezzanine.pages.middleware.PageMiddleware "
            "(or a subclass of it) is missing from "
            "settings.MIDDLEWARE"
        )

    if not hasattr(request, "page") or request.page.slug != slug:
        raise Http404

    # Check for a template name matching the page's slug. If the homepage
    # is configured as a page instance, the template "pages/index.html" is
    # used, since the slug "/" won't match a template name.
    template_name = str(slug) if slug != home_slug() else "index"
    templates = ["pages/%s.html" % template_name]
    method_template = request.page.get_content_model().get_template_name()
    if method_template:
        templates.insert(0, method_template)
    if request.page.content_model is not None:
        templates.append(f"pages/{template_name}/{request.page.content_model}.html")
    for parent in request.page.get_ascendants(for_user=request.user):
        parent_template_name = str(parent.slug)
        # Check for a template matching the page's content model.
        if request.page.content_model is not None:
            templates.append(
                f"pages/{parent_template_name}/{request.page.content_model}.html"
            )
    # Check for a template matching the page's content model.
    if request.page.content_model is not None:
        templates.append("pages/%s.html" % request.page.content_model)
    templates.append(template)
    return TemplateResponse(request, templates, extra_context or {})
