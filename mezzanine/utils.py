
from htmlentitydefs import name2codepoint
from re import sub

from django.core.paginator import Paginator, InvalidPage, EmptyPage


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

