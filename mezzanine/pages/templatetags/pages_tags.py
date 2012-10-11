
from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template import TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from mezzanine.pages.models import Page
from mezzanine.utils.urls import admin_url
from mezzanine import template


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
        try:
            user = context["request"].user
            slug = context["request"].path
        except KeyError:
            user = None
            slug = ""
        num_children = lambda id: lambda: len(context["menu_pages"][id])
        has_children = lambda id: lambda: num_children(id)() > 0
        published = Page.objects.published(for_user=user)
        if slug == admin_url(Page, "changelist"):
            related = [m.__name__.lower() for m in Page.get_content_models()]
            published = published.select_related(*related)
        else:
            published = published.select_related(depth=2)
        # Store the current page being viewed in the context. Used
        # for comparisons in page.set_menu_helpers.
        if "page" not in context:
            try:
                context["_current_page"] = published.get(slug=slug)
            except Page.DoesNotExist:
                context["_current_page"] = None
        elif slug:
            context["_current_page"] = context["page"]
        # Maintain a dict of page IDs -> parent IDs for fast
        # lookup in setting page.is_current_or_ascendant in
        # page.set_menu_helpers.
        context["_parent_page_ids"] = {}
        pages = defaultdict(list)
        for page in published.order_by("_order"):
            page.set_helpers(context)
            context["_parent_page_ids"][page.id] = page.parent_id
            setattr(page, "num_children", num_children(page.id))
            setattr(page, "has_children", has_children(page.id))
            pages[page.parent_id].append(page)
        context["menu_pages"] = pages
        context["on_home"] = slug == reverse("home")
    # ``branch_level`` must be stored against each page so that the
    # calculation of it is correctly applied. This looks weird but if we do
    # the ``branch_level`` as a separate arg to the template tag with the
    # addition performed on it, the addition occurs each time the template
    # tag is called rather than once per level.
    context["branch_level"] = 0
    parent_page_id = None
    if parent_page is not None:
        context["branch_level"] = getattr(parent_page, "branch_level", 0) + 1
        parent_page_id = parent_page.id

    # Build the ``page_branch`` template variable, which is the list of
    # pages for the current parent. Here we also assign the attributes
    # to the page object that determines whether it belongs in the
    # current menu template being rendered.
    context["page_branch"] = context["menu_pages"].get(parent_page_id, [])
    context["page_branch_in_menu"] = False
    for page in context["page_branch"]:
        page.in_menu = page.in_menu_template(template_name)
        page.num_children_in_menu = 0
        if page.in_menu:
            context["page_branch_in_menu"] = True
        for child in context["menu_pages"].get(page.id, []):
            if child.in_menu_template(template_name):
                page.num_children_in_menu += 1
        page.has_children_in_menu = page.num_children_in_menu > 0
        page.branch_level = context["branch_level"]
        page.parent = parent_page

        # Prior to pages having the ``in_menus`` field, pages had two
        # boolean fields ``in_navigation`` and ``in_footer`` for
        # controlling menu inclusion. Attributes and variables
        # simulating these are maintained here for backwards
        # compatibility in templates, but will be removed eventually.
        page.in_navigation = page.in_menu
        page.in_footer = not (not page.in_menu and "footer" in template_name)
        if page.in_navigation:
            context["page_branch_in_navigation"] = True
        if page.in_footer:
            context["page_branch_in_footer"] = True

    t = get_template(template_name)
    return t.render(context)


@register.as_tag
def models_for_pages(*args):
    """
    Create a select list containing each of the models that subclass the
    ``Page`` model.
    """
    page_models = []
    for model in Page.get_content_models():
        try:
            admin_url(model, "add")
        except NoReverseMatch:
            continue
        else:
            setattr(model, "name", model._meta.verbose_name)
            setattr(model, "add_url", admin_url(model, "add"))
            page_models.append(model)
    return page_models


@register.render_tag
def set_model_permissions(context, token):
    """
    Assigns a permissions dict to the given model, much like Django
    does with its dashboard app list.

    Used within the change list for pages, to implement permission
    checks for the navigation tree.
    """
    model = context[token.split_contents()[1]]
    opts = model._meta
    perm_name = opts.app_label + ".%s_" + opts.object_name.lower()
    request = context["request"]
    setattr(model, "perms", {})
    for perm_type in ("add", "change", "delete"):
        model.perms[perm_type] = request.user.has_perm(perm_name % perm_type)
    return ""


@register.render_tag
def set_page_permissions(context, token):
    """
    Assigns a permissions dict to the given page instance, combining
    Django's permission for the page's model and a permission check
    against the instance itself calling the page's ``can_add``,
    ``can_change`` and ``can_delete`` custom methods.

    Used within the change list for pages, to implement permission
    checks for the navigation tree.
    """
    page = context[token.split_contents()[1]]
    model = page.get_content_model()
    try:
        opts = model._meta
    except AttributeError:
        # A missing inner Meta class usually means the Page model
        # hasn't been directly subclassed.
        error = _("An error occured with the following class. Does "
                  "it subclass Page directly?")
        raise ImproperlyConfigured(error + " '%s'" % model.__class__.__name__)
    perm_name = opts.app_label + ".%s_" + opts.object_name.lower()
    request = context["request"]
    setattr(page, "perms", {})
    for perm_type in ("add", "change", "delete"):
        perm = request.user.has_perm(perm_name % perm_type)
        perm = perm and getattr(model, "can_%s" % perm_type)(request)
        page.perms[perm_type] = perm
    return ""
