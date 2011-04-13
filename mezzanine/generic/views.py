
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from mezzanine.generic.models import Keyword


@staff_member_required
def admin_keywords_submit(request):
    """
    Adds any new given keywords from the custom keywords field in the 
    admin, and returns their IDs for use when saving a model with a 
    keywords field.
    """
    ids = []
    for title in request.POST.get("text_keywords", "").split(","):
        title = "".join([c for c in title if c.isalnum() or c == "-"]).lower()
        if title:
            keyword, created = Keyword.objects.get_or_create(title=title)
            ids.append(str(keyword.id))
    return HttpResponse(",".join(set(ids)))
