from __future__ import unicode_literals
from future.builtins import str

from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from mezzanine.pages.models import Page
from mezzanine.utils.urls import home_slug
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
        if isinstance(part, str):
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
        rel = [m.__name__.lower()
               for m in Page.get_content_models()
               if not m._meta.proxy]
        published = Page.objects.published(for_user=user).select_related(*rel)
        # Store the current page being viewed in the context. Used
        # for comparisons in page.set_menu_helpers.
        if "page" not in context:
            try:
                context.dicts[0]["_current_page"] = published.exclude(
                    content_model="link").get(slug=slug)
            except Page.DoesNotExist:
                context.dicts[0]["_current_page"] = None
        elif slug:
            context.dicts[0]["_current_page"] = context["page"]
        # Some homepage related context flags. on_home is just a helper
        # indicated we're on the homepage. has_home indicates an actual
        # page object exists for the homepage, which can be used to
        # determine whether or not to show a hard-coded homepage link
        # in the page menu.
        home = home_slug()
        context.dicts[0]["on_home"] = slug == home
        context.dicts[0]["has_home"] = False
        # Maintain a dict of page IDs -> parent IDs for fast
        # lookup in setting page.is_current_or_ascendant in
        # page.set_menu_helpers.
        context.dicts[0]["_parent_page_ids"] = {}
        pages = defaultdict(list)
        for page in published.order_by("_order"):
            page.set_helpers(context)
            context["_parent_page_ids"][page.id] = page.parent_id
            setattr(page, "num_children", num_children(page.id))
            setattr(page, "has_children", has_children(page.id))
            pages[page.parent_id].append(page)
            if page.slug == home:
                context.dicts[0]["has_home"] = True
        # Include menu_pages in all contexts, not only in the
        # block being rendered.
        context.dicts[0]["menu_pages"] = pages
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
        context["parent_page"] = page.parent

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
    return t.render(context.flatten())


@register.as_tag
def models_for_pages(*args):
    """
    Create a select list containing each of the models that subclass the
    ``Page`` model.
    """
    from warnings import warn
    warn("template tag models_for_pages is deprectaed, use "
        "PageAdmin.get_content_models instead")
    from mezzanine.pages.admin import PageAdmin
    return PageAdmin.get_content_models()


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
        if model is None:
            error = _("Could not load the model for the following page, "
                      "was it removed?")
            obj = page
        else:
            # A missing inner Meta class usually means the Page model
            # hasn't been directly subclassed.
            error = _("An error occured with the following class. Does "
                      "it subclass Page directly?")
            obj = model.__class__.__name__
        raise ImproperlyConfigured(error + " '%s'" % obj)
    perm_name = opts.app_label + ".%s_" + opts.object_name.lower()
    request = context["request"]
    setattr(page, "perms", {})
    for perm_type in ("add", "change", "delete"):
        perm = request.user.has_perm(perm_name % perm_type)
        perm = perm and getattr(model, "can_%s" % perm_type)(request)
        page.perms[perm_type] = perm
    return ""
