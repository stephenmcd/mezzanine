
from django import template


class Library(template.Library):
    """
    Drop-in replacement for django.template.Library providing several 
    shortcuts that attempt to take the leg-work out of creating different 
    types of template tags.
    """
    
    def _make_tag_type(self, func_from, func_to):
        """
        Copy attributes from the original tag func to the wrapper tag func 
        containing the tag's node class, and return it as a new template tag.
        """
        for copy_attr in ("__dict__", "__doc__", "__name__"):
            setattr(func_to, copy_attr, getattr(func_from, copy_attr))
        return self.tag(func_to)
    
    def as_tag(self, func):
        """
        Creates a tag expecting the format: ``{% tag_name as var_name %}`` 
        The decorated func returns the value that is given to ``var_name`` in 
        the template.
        """
        def tag(parser, token):
            class TagNode(template.Node):
                def render(self, context):
                    parts = token.split_contents()
                    context[parts[-1]] = func(*parts[1:-2])
                    return ""
            return TagNode()
        return self._make_tag_type(func, tag)

    def render_tag(self, func):
        """
        Creates a tag using the decorated func as the render function for the 
        template tag node. The render function takes two arguments - the 
        template context and the tag token.
        """
        def tag(parser, token):
            class TagNode(template.Node):
                def render(self, context):
                    return func(context, token)
            return TagNode()
        return self._make_tag_type(func, tag)

    def to_end_tag(self, func):
        """
        Creates a tag that parses until it finds the corresponding end tag, 
        eg: for a tag named ``mytag`` it will parse until ``endmytag``. 
        The decorated func takes a single argument which is the parsed content 
        between the start and end tags, and its return value is used to render 
        the parsed content.
        """
        def tag(parser, token):
            class TagNode(template.Node):
                def __init__(self):
                    self.nodelist = parser.parse(("end%s" % func.__name__,))
                    parser.delete_first_token()
                def render(self, context):
                    return func(self.nodelist.render(context))
            return TagNode()
        return self._make_tag_type(func, tag)

