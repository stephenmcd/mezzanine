
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template

from mezzanine.pages.models import Page


def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """
    for i, page in enumerate(request.POST.get("ordering", "").split(",")):
        try:
            Page.objects.filter(id=page.split("_")[-1]).update(ordering=i)
        except ValueError:
            pass
    return HttpResponse("")
admin_page_ordering = staff_member_required(admin_page_ordering)

def page(request, slug, template="pages/page.html"):
    """
    Display content for a page.
    """
    page = get_object_or_404(Page.objects.published(request.user), slug=slug)
    context = {"page": page,}
    t = select_template(["pages/%s.html" % slug, template])
    return HttpResponse(t.render(RequestContext(request, context)))

