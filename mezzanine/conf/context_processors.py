

def settings(request):
    """
    Add the settings object to the template context.
    """
    from mezzanine.conf import settings
    settings.use_editable()
    return {"settings": settings}
