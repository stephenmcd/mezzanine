
from collections import defaultdict

from django.core.urlresolvers import reverse
from django.db.models import get_model, get_models

from mezzanine.pages.models import Page
from mezzanine.utils import admin_url
from mezzanine import template


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
        try:
            slug = context["request"].path.strip("/")
        except KeyError:
            slug = ""
        for page in Page.objects.published(for_user=user).order_by("_order"):
            setattr(page, "selected", (slug + "/").startswith(page.slug + "/"))
            setattr(page, "html_id", page.slug.replace("/", "-"))
            setattr(page, "primary", page.parent_id is None)
            setattr(page, "branch_level", 0)
            pages[page.parent_id].append(page)
        context["menu_pages"] = pages
    # ``branch_level`` must be stored against each page so that the 
    # calculation of it is correctly applied. This looks weird but if we do 
    # the ``branch_level`` as a separate arg to the template tag with the 
    # addition performed on it, the addition occurs each time the template 
    # tag is called rather than once per level.
    context["branch_level"] = 0
    if parent_page is not None:
        context["branch_level"] = parent_page.branch_level + 1
        parent_page = parent_page.id
    context["page_branch"] = context["menu_pages"].get(parent_page, [])
    for i, page in enumerate(context["page_branch"]):
        context["page_branch"][i].branch_level = context["branch_level"]
    return context


@register.inclusion_tag("pages/includes/tree_menu.html", takes_context=True)
def tree_menu(context, parent_page=None):
    """
    Tree menu that renders all pages in the navigation hierarchically.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("pages/includes/tree_menu_footer.html", takes_context=True)
def tree_menu_footer(context, parent_page=None):
    """
    Tree menu that renders all pages in the footer hierarchically.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("pages/includes/primary_menu.html", takes_context=True)
def primary_menu(context, parent_page=None):
    """
    Page menu that only renders the primary top-level pages.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("pages/includes/footer_menu.html", takes_context=True)
def footer_menu(context, parent_page=None):
    """
    Page menu that only renders the footer pages.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("pages/includes/breadcrumb_menu.html", 
    takes_context=True)
def breadcrumb_menu(context, parent_page=None):
    """
    Page menu that only renders the pages that are parents of the current 
    page, as well as the current page itself.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("admin/includes/tree_menu.html", takes_context=True)
def tree_menu_admin(context, parent_page=None):
    """
    Admin tree menu for managing pages.
    """
    return _page_menu(context, parent_page)


@register.as_tag
def models_for_pages(*args):
    """
    Create a select list containing each of the models that subclass the
    ``Page`` model.
    """
    page_models = []
    for model in get_models():
        if model is not Page and issubclass(model, Page):
            setattr(model, "name", model._meta.verbose_name)
            setattr(model, "add_url", admin_url(model, "add"))
            page_models.append(model)
    return page_models


@register.filter
def is_page_content_model(admin_model_dict):
    """
    Returns True if the model in the given admin dict is a subclass of the
    ``Page`` model.
    """
    args = admin_model_dict["admin_url"].strip("/").split("/")
    if len(args) == 2:
        model = get_model(*args)
        return model is not Page and issubclass(model, Page)
    return False
