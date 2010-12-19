
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.utils.http import urlquote

from mezzanine.conf import settings
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page
from mezzanine.template.loader import select_template


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


def page(request, slug, template="pages/page.html"):
    """
    Display content for a page. First check for any matching page processors
    and handle them. Secondly, build the list of template names to choose
    from given the slug and type of page being viewed.
    """
    page = get_object_or_404(Page.objects.published(request.user), slug=slug)
    if page.login_required and not request.user.is_authenticated():
        return redirect("%s?%s=%s" % (settings.LOGIN_URL, REDIRECT_FIELD_NAME,
            urlquote(request.get_full_path())))
    context = {"page": page}
    for processor in page_processors.processors[page.content_model]:
        response = processor(request, page)
        if isinstance(response, HttpResponse):
            return response
        elif response:
            if isinstance(response, dict):
                context.update(response)
            else:
                raise ValueError("The page processor %s.%s returned %s but "
                    "must return HttpResponse or dict." % (
                    processor.__module__, processor.__name__, type(response)))
    templates = ["pages/%s.html" % slug]
    if page.content_model is not None:
        templates.append("pages/%s.html" % page.content_model)
    templates.append(template)
    request_context = RequestContext(request, context)
    t = select_template(templates, request_context)
    return HttpResponse(t.render(request_context))
