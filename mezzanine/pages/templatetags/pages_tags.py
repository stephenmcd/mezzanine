import re
from collections import defaultdict

from django import template
from django.core.urlresolvers import reverse
from django.db.models import get_model, get_models

from mezzanine import template
from mezzanine.pages.models import Page
from mezzanine.settings import PAGES_MENU_SHOW_ALL

register = template.Library()

try:
    from template_utils.templatetags import comparison
    for tag_name in comparison.COMPARISON_DICT:
        register.tag('if_%s' % tag_name, comparison.do_comparison)
except ImportError:
    # We don't have django template utils. Bring in just enough to make this work.
    # Copied from django template utils, <http://code.google.com/p/django-template-utils/>
    # Licensed under the BSD license.

    COMPARISON_DICT = {
      'startswith': lambda x,y: x.startswith(y),
      'endswith': lambda x,y: x.endswith(y),
      'find': lambda x,y: x.find(y) >- 1,
      'match': lambda x,y: re.compile(y).match(x),
    }

    class ComparisonNode(template.Node):
        def __init__(self, comparison, nodelist_true, nodelist_false, negate, *vars):
            self.vars = map(template.Variable, vars)
            self.comparison = comparison
            self.negate = negate
            self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

        def render(self, context):
            try:
                if COMPARISON_DICT[self.comparison](
                  *[var.resolve(context) for var in self.vars]):
                    if self.negate:
                        return self.nodelist_false.render(context)
                    return self.nodelist_true.render(context)
            # If either variable fails to resolve, return nothing.
            except template.VariableDoesNotExist:
                return ''
            # If the types don't permit comparison, return nothing.
            except TypeError:
                return ''
            if self.negate:
                return self.nodelist_true.render(context)
            return self.nodelist_false.render(context)

    def do_comparison(parser, token):
        """
        Compares two values.

        Syntax::

            {% if_[comparison] [var1] [var2] [var...] %}
            ...
            {% else %}
            ...
            {% endif_[comparison] %}

        The {% else %} block is optional, and any ``var`` may be
        variables or literal values.
        """
        negate = False
        bits = token.contents.split()
        end_tag = 'end' + bits[0]
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else':
            nodelist_false = parser.parse((end_tag,))
            parser.delete_first_token()
        else:
            nodelist_false = template.NodeList()
        if bits[-1] == 'negate':
            bits = bits[:-1]
            negate = True
        comparison = bits[0].split('if_')[1]
        return ComparisonNode(comparison, nodelist_true, nodelist_false, negate, *bits[1:])

    for tag_name in COMPARISON_DICT:
        register.tag('if_%s' % tag_name, do_comparison)

### End portion copied from django template utils

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


@register.inclusion_tag("pages/includes/toplevel_menu.html", takes_context=True)
def toplevel_menu(context, parent_page=None):
    """
    Toplevel page menu for main nav. Never includes subtrees.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("pages/includes/breadcrumbs.html", takes_context=True)
def breadcrumbs(context, parent_page=None):
    """
    Provides a unordered list from Home down to the current page in the hierarchy.
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
