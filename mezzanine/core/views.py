
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from mezzanine.core.models import Keyword


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

