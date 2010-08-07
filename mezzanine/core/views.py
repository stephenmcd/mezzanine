
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import get_model
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.forms import get_edit_form
from mezzanine.core.models import Keyword, Displayable
from mezzanine.settings import SEARCH_MAX_PAGING_LINKS, SEARCH_PER_PAGE
from mezzanine.utils import is_editable, paginate


def admin_keywords_submit(request):
    """
    Adds any new given keywords from the custom keywords field in the admin and
    returns their IDs for use when saving a model with a keywords field.
    """
    ids = []
    for value in request.POST.get("text_keywords", "").split(","):
        value = "".join([c for c in value if c.isalnum() or c == "-"]).lower()
        if value:
            keyword, created = Keyword.objects.get_or_create(value=value)
            ids.append(str(keyword.id))
    return HttpResponse(",".join(set(ids)))
admin_keywords_submit = staff_member_required(admin_keywords_submit)


def search(request, template="search_results.html"):
    """
    Display search results.
    """
    query = request.GET.get("q", "")
    results = Displayable.objects.search(query)
    results = paginate(results, request.GET.get("page", 1), SEARCH_PER_PAGE,
        SEARCH_MAX_PAGING_LINKS)
    context = {"query": query, "results": results}
    return render_to_response(template, context, RequestContext(request))


def edit(request):
    model = get_model(request.POST["app"], request.POST["model"])
    obj = model.objects.get(id=request.POST["id"])
    form = get_edit_form(obj, request.POST["attr"], data=request.POST)
    if not is_editable(obj, request):
        response = _("Permission denied")
    elif form.is_valid():
        form.save()
        response = ""
    else:
        response = form.errors.values()[0][0]
    return HttpResponse(unicode(response))
