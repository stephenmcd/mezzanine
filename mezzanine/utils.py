
from htmlentitydefs import name2codepoint
from re import sub

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor


def decode_html_entities(html):
    """
    Remove HTML entities from a string.
    Adapted from http://effbot.org/zone/re-sub.htm#unescape-html
    """
    def decode(m):
        html = m.group(0)
        if html[:2] == "&#":
            try:
                if html[:3] == "&#x":
                    return unichr(int(html[3:-1], 16))
                else:
                    return unichr(int(html[2:-1]))
            except ValueError:
                pass
        else:
            try:
                html = unichr(name2codepoint[html[1:-1]])
            except KeyError:
                pass
        return html
    return sub("&#?\w+;", decode, html.replace("&amp;", "&"))


def is_editable(obj, request):
    """
    Returns True if the object is editable for the request. First check for
    a custom ``editable`` handler on the object, otherwise use the logged
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


def base_concrete_model(abstract, instance):
    """
    Used in methods of abstract models to find the super-most concrete
    (non abstract) model in the inheritence chain that inherits from the
    given abstract model. This is so the methods in the abstract model can
    query data consistantly across the correct concrete model.

    Consider the following::

        class Abstract(models.Model)

            class Meta:
                abstract = True

            def concrete(self):
                return concrete_model_for(Abstract, self)

        class Super(Abstract):
            pass

        class Sub(Super):
            pass

        sub = Sub.objects.create()
        sub.real_obj() # returns Super

    In actual Mezzanine usage, this allows methods in the ``Displayable`` and
    ``Orderable`` abstract models to access the ``Page`` instance when
    instances of custom content types, (eg: models that inherit from ``Page``)
    need to query the ``Page`` model to determine correct values for ``slug``
    and ``_order`` which are only relevant in the context of the ``Page``
    model and not the model of the custom content type.
    """
    for cls in reversed(instance.__class__.__mro__):
        if issubclass(cls, abstract) and not cls._meta.abstract:
            return cls
    return instance.__class__
