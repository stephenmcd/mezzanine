"""
Backward compatible user messaging functions.
"""


def message_fallback(request, message, extra_tags="", fail_silently=False):
    """
    Fallback for Django prior to ``django.contrib.messages``.
    """
    if request.user.is_authenticated() or not fail_silently:
        request.user.message_set.create(message=message)

try:
    from django.contrib.messages import debug, info, success, warning, error
except ImportError:
    debug = info = success = warning = error = message_fallback
