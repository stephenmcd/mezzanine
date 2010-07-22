
from mezzanine import template

register = template.Library()

@register.simple_tag
def csrf_token():
    return ""

