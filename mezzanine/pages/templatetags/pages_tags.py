
from collections import defaultdict

from django.core.urlresolvers import reverse
from django.db.models import get_models
from django.template import TemplateSyntaxError, Variable

from mezzanine.pages.models import Page
from mezzanine.utils.urls import admin_url
from mezzanine import template
from mezzanine.template.loader import get_template


register = template.Library()


@register.render_tag
def page_menu(context, token):
    """
    Return a list of child pages for the given parent, storing all
    pages in a dict in the context when first called using parents as keys
    for retrieval on subsequent recursive calls from the menu template.
    """
    # First arg could be the menu template file name, or the parent page.
    # Also allow for both to be used.
    template_name = None
    parent_page = None
    parts = token.split_contents()[1:]
    for part in parts:
        part = Variable(part).resolve(context)
        if isinstance(part, unicode):
            template_name = part
        elif isinstance(part, Page):
            parent_page = part
    if template_name is None:
        try:
            template_name = context["menu_template_name"]
        except KeyError:
            error = "No template found for page_menu in: %s" % parts
            raise TemplateSyntaxError(error)
    context["menu_template_name"] = template_name
    if "menu_pages" not in context:
        pages = defaultdict(list)
        try:
            user = context["request"].user
            slug = context["request"].path
        except KeyError:
            user = None
            slug = ""
        for page in Page.objects.published(for_user=user).order_by("_order"):
            page.set_menu_helpers(slug)
            pages[page.parent_id].append(page)
        context["menu_pages"] = pages
        context["on_home"] = slug == reverse("home")
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
    t = get_template(template_name, context)
    return t.render(context)


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
