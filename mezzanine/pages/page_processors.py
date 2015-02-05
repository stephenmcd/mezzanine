from __future__ import unicode_literals
from future.builtins import str as _str

from collections import defaultdict

from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from mezzanine.conf import settings
from mezzanine.pages.models import Page
from mezzanine.utils.models import get_model


processors = defaultdict(list)


def processor_for(content_model_or_slug, exact_page=False):
    """
    Decorator that registers the decorated function as a page
    processor for the given content model or slug.

    When a page exists that forms the prefix of custom urlpatterns
    in a project (eg: the blog page and app), the page will be
    added to the template context. Passing in ``True`` for the
    ``exact_page`` arg, will ensure that the page processor is not
    run in this situation, requiring that the loaded page object
    is for the exact URL currently being viewed.
    """
    content_model = None
    slug = ""
    if isinstance(content_model_or_slug, (str, _str)):
        try:
            content_model = get_model(*content_model_or_slug.split(".", 1))
        except (TypeError, ValueError, LookupError):
            slug = content_model_or_slug
    elif issubclass(content_model_or_slug, Page):
        content_model = content_model_or_slug
    else:
        raise TypeError("%s is not a valid argument for page_processor, "
                        "which should be a model subclass of Page in class "
                        "or string form (app.model), or a valid slug" %
                        content_model_or_slug)

    def decorator(func):
        parts = (func, exact_page)
        if content_model:
            model_name = content_model._meta.object_name.lower()
            processors[model_name].insert(0, parts)
        else:
            processors["slug:%s" % slug].insert(0, parts)
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
        module = import_module(app)
        try:
            import_module("%s.page_processors" % app)
        except:
            if module_has_submodule(module, "page_processors"):
                raise
