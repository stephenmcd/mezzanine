
from collections import defaultdict

from django.db.models import get_model

from mezzanine.conf import settings
from mezzanine.pages.models import Page


processors = defaultdict(list)


def processor_for(content_model):
    """
    Decorator that registers the decorated function as a page processor for
    the given content model.
    """
    if isinstance(content_model, basestring):
        content_model = get_model(*content_model.split("."))
    if not issubclass(content_model, Page):
        raise TypeError("%s is not a subclass of Page" % content_model)
    def decorator(func):
        processors[content_model._meta.object_name.lower()].append(func)
        return func
    return decorator

LOADED = False


def autodiscover():
    """
    Taken from ``django.contrib.admin.autodiscover`` and used to run any
    calls to the ``processor_for`` decorator.
    """
    global LOADED
    if LOADED:
        return
    LOADED = True
    for app in settings.INSTALLED_APPS:
        try:
            __import__("%s.page_processors" % app)
        except ImportError:
            pass
