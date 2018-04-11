from __future__ import unicode_literals

from functools import wraps
import warnings

from django import template
from django import VERSION as DJANGO_VERSION


class Library(template.Library):
    """
    Extends ``django.template.Library`` providing several shortcuts
    that attempt to take the leg-work out of creating different types
    of template tags.
    """

    def as_tag(self, tag_func):
        """
        Creates a tag expecting the format:
        ``{% tag_name as var_name %}``
        The decorated func returns the value that is given to
        ``var_name`` in the template.
        """
        package = tag_func.__module__.split(".")[0]
        if DJANGO_VERSION >= (1, 9) and package != "mezzanine":
            warnings.warn(
                "The `as_tag` template tag builder is deprecated in favour of "
                "Django's built-in `simple_tag`, which supports variable "
                "assignment in Django 1.9 and above.",
                DeprecationWarning, stacklevel=2
            )

        @wraps(tag_func)
        def tag_wrapper(parser, token):
            class AsTagNode(template.Node):
                def render(self, context):
                    parts = token.split_contents()

                    # Resolve variables if their names are given.
                    def resolve(arg):
                        try:
                            return template.Variable(arg).resolve(context)
                        except template.VariableDoesNotExist:
                            return arg
                    args, kwargs = [], {}
                    for arg in parts[1:-2]:
                        if "=" in arg:
                            name, val = arg.split("=", 1)
                            if name in tag_func.__code__.co_varnames:
                                kwargs[name] = resolve(val)
                                continue
                        args.append(resolve(arg))
                    context[parts[-1]] = tag_func(*args, **kwargs)
                    return ""
            return AsTagNode()
        return self.tag(tag_wrapper)

    def render_tag(self, tag_func):
        """
        Creates a tag using the decorated func as the render function
        for the template tag node. The render function takes two
        arguments - the template context and the tag token.
        """
        @wraps(tag_func)
        def tag_wrapper(parser, token):
            class RenderTagNode(template.Node):
                def render(self, context):
                    return tag_func(context, token)
            return RenderTagNode()
        return self.tag(tag_wrapper)

    def to_end_tag(self, tag_func):
        """
        Creates a tag that parses until it finds the corresponding end
        tag, eg: for a tag named ``mytag`` it will parse until
        ``endmytag``. The decorated func's return value is used to
        render the parsed content and takes three arguments - the
        parsed content between the start and end tags, the template
        context and the tag token.
        """
        @wraps(tag_func)
        def tag_wrapper(parser, token):

            class ToEndTagNode(template.Node):

                def __init__(self):
                    end_name = "end%s" % tag_func.__name__
                    self.nodelist = parser.parse((end_name,))
                    parser.delete_first_token()

                def render(self, context):
                    args = (self.nodelist.render(context), context, token)
                    return tag_func(*args[:tag_func.__code__.co_argcount])

            return ToEndTagNode()

        return self.tag(tag_wrapper)
