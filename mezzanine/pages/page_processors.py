
from collections import defaultdict

from django.db.models import get_model

from mezzanine.conf import settings
from mezzanine.pages.models import Page


processors = defaultdict(list)


def processor_for(content_model_or_slug):
    """
    Decorator that registers the decorated function as a page
    processor for the given content model or slug.
    """
    content_model = None
    slug = ""
    if isinstance(content_model_or_slug, basestring):
        try:
            content_model = get_model(*content_model_or_slug.split(".", 1))
        except TypeError:
            slug = content_model_or_slug
    elif issubclass(content_model_or_slug, Page):
        content_model = content_model_or_slug
    else:
        raise TypeError("%s is not a valid argument for page_processor, "
                        "which should be a model subclass of Page in class "
                        "or string form (app.model), or a valid slug" %
                        content_model_or_slug)

    def decorator(func):
        if content_model:
            processors[content_model._meta.object_name.lower()].append(func)
        else:
            processors["slug:%s" % slug].append(func)
        return func
    return decorator


LOADED = False


def autodiscover():
    """
    Taken from ``django.contrib.admin.autodiscover`` and used to run
    any calls to the ``processor_for`` decorator.
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
