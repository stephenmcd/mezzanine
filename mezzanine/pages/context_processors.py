
from mezzanine.pages.models import Page


def page(request):
    """
    Adds the current page to the template context and runs its
    ``set_helper`` method. This was previously part of
    ``PageMiddleware``, but moved to a context processor so that
    we could assign these template context variables without
    the middleware depending on Django's ``TemplateResponse``.
    """
    context = {}
    page = getattr(request, "page", None)
    if isinstance(page, Page):
        # set_helpers has always expected the current template context,
        # but here we're just passing in our context dict with enough
        # variables to satisfy it.
        context = {"request": request, "page": page, "_current_page": page}
        page.set_helpers(context)
    return context
