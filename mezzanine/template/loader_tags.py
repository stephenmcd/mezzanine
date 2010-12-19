"""
This module redefines the template tags from ``django.template.loader_tags``
that deal with template loading, specifically ``extend`` and ``include``.
They're reproduced here to make use of Mezzanine's ``get_template`` which
handles device specific template loading.
"""

from django.conf import settings
from django.template import TemplateSyntaxError, Variable
from django.template.loader_tags import ExtendsNode

from mezzanine.template import Library
from mezzanine.template.loader import get_template


register = Library()


class ContextAwareExtendsNode(ExtendsNode):

    def get_parent(self, context):
        """
        Override to use Mezzanine's context-aware ``get_template``.
        """
        if self.parent_name_expr:
            self.parent_name = self.parent_name_expr.resolve(context)
        parent = self.parent_name
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name_expr:
                error_msg += (" Got this from the '%s' variable." %
                              self.parent_name_expr.token)
            raise TemplateSyntaxError(error_msg)
        if hasattr(parent, "render"):
            return parent  # parent is a Template object
        return get_template(parent, context)


@register.tag
def extends(parser, token):
    """
    Signal that this template extends a parent template.
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    parent_name, parent_name_expr = None, None
    if bits[1][0] in ('"', "'") and bits[1][-1] == bits[1][0]:
        parent_name = bits[1][1:-1]
    else:
        parent_name_expr = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(ContextAwareExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in "
                                  "the same template" % bits[0])
    return ContextAwareExtendsNode(nodelist, parent_name, parent_name_expr)


@register.render_tag
def include(context, token):
    """
    Loads a template and renders it with the current context.
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: "
                        "the name of the template to be included" % bits[0])
    template = bits[1]
    if template[0] in ('"', "'") and template[-1] == template[0]:
        template = template[1:-1]
    else:
        template = Variable(template).resolve(context)
    try:
        t = get_template(template, context)
        return t.render(context)
    except TemplateSyntaxError:
        if settings.TEMPLATE_DEBUG:
            raise
    return ""
