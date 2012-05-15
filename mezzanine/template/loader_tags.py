
from django.template import Template, TemplateSyntaxError
from django.template.loader_tags import ExtendsNode
from django.template.loader import get_template, find_template

from mezzanine import template


register = template.Library()


class OverExtendsNode(ExtendsNode):
    """
    Allows the template foo/bar.html to extend foo/bar.html, given
    that there is another version of it that can be loaded. This allows
    templates to be created in a project that extend their app template
    counterparts.

    We first load the template we're extending, which in the case of a
    circular extend, will be the same template the tag is being called
    in. We can then look at the first node of the loaded template, and
    compare its arg to the arg given within the call to this instance
    of extend. If they match, we then have a circular extend.

    Once a circular extend is detected, we then take advantage of the
    fact that each of the template loaders takes an optional list of
    directories to use. We then build a *full* list of template
    directories, given the known values the loaders use: app template
    directories, and the ``TEMPLATE_DIRS`` setting.

    With this full list, we can remove the directory that the loaded
    parent template used (accessible via its ``origin``), and pass the
    list of all template directories (minus one) to the template
    loaders. Since all directories are given, the first template loader
    should be able to find the intended parent, and use it.

    As a final step, we actually store the filtered directory list in a
    context dictionary for each template name this occurs for, and on
    subsequent runs for the same template name in a single page, we
    reuse this directory list, removing each absolute directory that
    gets used. This allows for inheritence to reach beyond a single
    step, so a project template can extend itself from a third-party
    app version, which extends itself from our own app's version.

    Works at least against Django's ``app_directories``, ``filesystem``
    and ``cached`` loaders.
    """

    def get_parent(self, context):

        # These imports want Django settings, which won't be available
        # when this module is imported to ``add_to_builtins``, so do
        #them here.
        from django.template.loaders.app_directories import app_template_dirs
        from mezzanine.conf import settings

        parent = self.parent_name.resolve(context)
        if hasattr(parent, "render"):
            # {% extends %} arg is a template object, just return it.
            return parent
        # {% extends %} arg is a template name, load it.
        t = get_template(parent)
        if t.nodelist and isinstance(t.nodelist[0], ExtendsNode):
            first_node_template = t.nodelist[0].parent_name.resolve(context)
            if first_node_template == parent:
                # First node in the parent is an extends tag, with the
                # same arg as this extends instance, so a circular
                # extend has been detected. Create a full list of
                # template directories, remove the loaded parent's
                # directory from it, and find the same template name
                # within the filtered list of template directories. We
                # also store the list of directories to reuse in the
                # template context, and remove each directory we use
                # each time a circular extend occurs. This way circular
                # inheritence can each beyond a single level.
                if not hasattr(t, "origin"):
                    # Template won't have an origin during tests, so
                    # we can't determine it s path - just bail out.
                    return Template("")
                template_dirname = lambda t: t.origin.name[:-len(parent) - 1]
                context_name = "OVEREXTENDS_DIRS"
                if context_name not in context:
                    context[context_name] = {}
                if parent not in context[context_name]:
                    all_dirs = list(app_template_dirs + settings.TEMPLATE_DIRS)
                    context[context_name][parent] = all_dirs
                    # This is the first circular extend for this
                    # template name. Remove the initial directory for
                    # the first inheritence step.
                    context[context_name][parent].remove(template_dirname(t))
                next = find_template(parent, context[context_name][parent])[0]
                # Remove the origin for the next parent (the one we'll
                # be using) from the cached list of available template
                # directories, so that it won't be used on subsequent
                # circular extends for this template name.
                context[context_name][parent].remove(template_dirname(next))
                return next
        return get_template(parent)


@register.tag
def overextends(parser, token):
    """
    Extended version of Django's {% extends %} tag that allows circular
    inheritance to occur, eg a template can both be overridden and
    extended at once.
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    parent_name = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once "
                                  "in the same template" % bits[0])
    return OverExtendsNode(nodelist, parent_name)
