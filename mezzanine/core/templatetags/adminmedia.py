
from mezzanine.conf import settings
from mezzanine import template


register = template.Library()


@register.simple_tag
def admin_media_prefix():
    """
    The ``ADMIN_MEDIA_PREFIX`` setting and this tag lib were removed
    from Django 1.5, but we still want them to handle Grappelli
    being optional.
    """
    return settings.ADMIN_MEDIA_PREFIX
