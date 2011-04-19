
from collections import defaultdict

from django.db.models import get_model

from mezzanine.conf import settings
from mezzanine.pages.models import Page


processors = defaultdict(list)


def processor_for(content_model=None, slug=None):
    """
    Decorator that registers the decorated function as a page 
    processor for the given content model.
    """
    if slug:
        page = Page.objects.get(slug=slug)
        if not page:
            raise TypeError("%s is not a valid Page slug" % slug)
    elif content_model:
        if isinstance(content_model, basestring):
            try:
                content_model = get_model(*content_model.split(".", 1))
            except ValueError:
                raise ValueError("%s isn't in the form: app.model" % content_model)
        if not issubclass(content_model, Page):
            raise TypeError("%s is not a subclass of Page" % content_model)
    def decorator(func):
        if slug:
            processors["slug:%s" % slug].append(func)    
        else:
            processors[content_model._meta.object_name.lower()].append(func)
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
