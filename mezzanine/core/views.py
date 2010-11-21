
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import get_model
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.forms import get_edit_form
from mezzanine.core.models import Keyword, Displayable
from mezzanine.utils import is_editable, paginate


def admin_keywords_submit(request):
    """
    Adds any new given keywords from the custom keywords field in the admin and
    returns their IDs for use when saving a model with a keywords field.
    """
    ids = []
    for title in request.POST.get("text_keywords", "").split(","):
        title = "".join([c for c in title if c.isalnum() or c == "-"]).lower()
        if title:
            keyword, created = Keyword.objects.get_or_create(title=title)
            ids.append(str(keyword.id))
    return HttpResponse(",".join(set(ids)))
admin_keywords_submit = staff_member_required(admin_keywords_submit)


def search(request, template="search_results.html"):
    """
    Display search results.
    """
    settings.use_editable()
    query = request.GET.get("q", "")
    results = Displayable.objects.search(query)
    results = paginate(results, request.GET.get("page", 1), 
        settings.SEARCH_PER_PAGE, settings.SEARCH_MAX_PAGING_LINKS)
    context = {"query": query, "results": results}
    return render_to_response(template, context, RequestContext(request))


def edit(request):
    """
    Process the inline editing form.
    """
    model = get_model(request.POST["app"], request.POST["model"])
    obj = model.objects.get(id=request.POST["id"])
    form = get_edit_form(obj, request.POST["fields"], data=request.POST,
                        files=request.FILES)
    if not is_editable(obj, request):
        response = _("Permission denied")
    elif form.is_valid():
        form.save()
        model_admin = ModelAdmin(model, admin.site)
        message = model_admin.construct_change_message(request, form, None)
        model_admin.log_change(request, obj, message)
        response = ""
    else:
        response = form.errors.values()[0][0]
    return HttpResponse(unicode(response))
