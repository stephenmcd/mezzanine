
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.http import urlquote

from mezzanine.conf import settings
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page


page_processors.autodiscover()


def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """
    for i, page in enumerate(request.POST.get("ordering", "").split(",")):
        try:
            Page.objects.filter(id=page.split("_")[-1]).update(_order=i)
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
    t = select_template(templates)
    return HttpResponse(t.render(RequestContext(request, context)))
