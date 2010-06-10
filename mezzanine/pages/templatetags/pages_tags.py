
from collections import defaultdict

from django import template

from mezzanine.pages.models import Page


register = template.Library()


def _page_menu(context, parent_page, page_qs):
    """
    Return a list of child pages for the given parent, storing all 
    pages in a dict in the context when first called using parents as keys 
    for retrieval on subsequent recursive calls from the menu template.
    """
    if "menu_pages" not in context:
        pages = defaultdict(list)
        for page in page_qs.order_by("ordering"):
            pages[page.parent_id].append(page)
        context["menu_pages"] = pages
    if parent_page is not None:
        parent_page = parent_page.id
    context["page_branch"] = context["menu_pages"].get(parent_page, [])
    return context

@register.inclusion_tag("pages/includes/page_menu.html", takes_context=True)
def page_menu(context, parent_page=None):
    """
    Public page menu.
    """
    return _page_menu(context, parent_page, 
        Page.objects.published(for_user=context["request"].user))

@register.inclusion_tag("admin/includes/page_menu.html", takes_context=True)
def page_menu_admin(context, parent_page=None):
    """
    Admin page menu.
    """
    return _page_menu(context, parent_page, 
        Page.objects.published(for_user=context["request"].user))
