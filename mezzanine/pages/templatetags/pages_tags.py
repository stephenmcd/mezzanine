
from collections import defaultdict

from django import template
from django.core.urlresolvers import reverse
from django.db.models import get_model, get_models

from mezzanine import template
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
        for page in Page.objects.published(for_user=user).order_by("_order"):
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

@register.as_tag
def models_for_pages(*args):
    """
    Create a select list containing each of the models that subclass the 
    ``Page`` model.
    """
    page_models = []
    for model in get_models():
        if issubclass(model, Page):
            setattr(model, "name", model._meta.verbose_name)
            setattr(model, "add_url", reverse("admin:%s_%s_add" % 
                (model._meta.app_label, model.__name__.lower())))
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

