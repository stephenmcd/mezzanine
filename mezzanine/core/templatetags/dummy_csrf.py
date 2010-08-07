
from mezzanine import template

register = template.Library()


@register.simple_tag
def csrf_token():
    """
    Dummy template tag that gets added to builtins in ``settings.py`` if the
    csrf middleware doesn't exist (< Django 1.2).
    """
    return ""
