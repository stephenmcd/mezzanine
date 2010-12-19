

def settings(request):
    """
    Add the settings object to the template context.
    """
    from mezzanine.conf import settings
    settings.use_editable()
    settings_dict = dict([(k, getattr(settings, k))
                          for k in settings.TEMPLATE_ACCESSIBLE_SETTINGS])
    return {"settings": type("Settings", (), settings_dict)}
