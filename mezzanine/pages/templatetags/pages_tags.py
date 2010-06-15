
from collections import defaultdict

from django import template

from mezzanine.pages.models import Page
from mezzanine.settings import PAGES_MENU_SHOW_ALL


register = template.Library()


def _page_menu(context, parent_page):
    """
    Return a list of child pages for the given parent, storing all 
    pages in a dict in the context when first called using parents as keys 
    for retrieval on subsequent recursive calls from the menu template.
    """
    if "menu_pages" not in context:
        pages = defaultdict(list)
        try:
            user = context["request"].user
        except KeyError:
            user = None
        for page in Page.objects.published(for_user=user).order_by("ordering"):
            try:
                slug = context["request"].path.strip("/")
            except KeyError:
                slug = ""
            setattr(page, "selected", slug.startswith(page.slug))
            pages[page.parent_id].append(page)
        context["menu_pages"] = pages
    if parent_page is not None:
        parent_page = parent_page.id
    context["page_branch"] = context["menu_pages"].get(parent_page, [])
    context["PAGES_MENU_SHOW_ALL"] = PAGES_MENU_SHOW_ALL
    return context

@register.inclusion_tag("pages/includes/page_menu.html", takes_context=True)
def page_menu(context, parent_page=None):
    """
    Public page menu.
    """
    return _page_menu(context, parent_page)

@register.inclusion_tag("admin/includes/page_menu.html", takes_context=True)
def page_menu_admin(context, parent_page=None):
    """
    Admin page menu.
    """
    return _page_menu(context, parent_page)

