
from datetime import datetime, timedelta

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.template import Context

from mezzanine.template.loader import get_template, select_template


def is_editable(obj, request):
    """
    Returns ``True`` if the object is editable for the request. First check 
    for a custom ``editable`` handler on the object, otherwise use the logged
    in user and check change permissions for the object's model.
    """
    if hasattr(obj, "is_editable"):
        return obj.is_editable(request)
    else:
        perm = obj._meta.app_label + "." + obj._meta.get_change_permission()
        return request.user.is_authenticated() and request.user.has_perm(perm)

        
def paginate(objects, page_num, per_page, max_paging_links):
    """
    Return a paginated page for the given objects, giving it a custom
    ``visible_page_range`` attribute calculated from ``max_paging_links``.
    """
    paginator = Paginator(list(objects), per_page)
    try:
        page_num = int(page_num)
    except ValueError:
        page_num = 1
    try:
        objects = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
    page_range = objects.paginator.page_range
    if len(page_range) > max_paging_links:
        start = min(objects.paginator.num_pages - max_paging_links,
            max(0, objects.number - (max_paging_links / 2) - 1))
        page_range = page_range[start:start + max_paging_links]
    objects.visible_page_range = page_range
    return objects


def render_to_response(template_name, dictionary=None, context_instance=None, 
                       mimetype=None):
    """
    Mimics ``django.shortcuts.render_to_response`` but uses Mezzanine's 
    ``get_template`` which handles device specific template directories.
    """
    dictionary = dictionary or {}
    if context_instance:
        context_instance.update(dictionary)
    else:
        context_instance = Context(dictionary)
    if isinstance(template_name, (list, tuple)):
        t = select_template(template_name, context_instance)
    else:
        t = get_template(template_name, context_instance)
    return HttpResponse(t.render(context_instance), mimetype=mimetype)


def set_cookie(response, name, value, expiry_seconds):
    """
    Set cookie wrapper that allows number of seconds to be given as the 
    expiry time, and ensures values are correctly encoded.
    """
    expires = datetime.strftime(datetime.utcnow() +
                                timedelta(seconds=expiry_seconds), 
                                "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(name, value.encode("utf-8"), expires=expires)
