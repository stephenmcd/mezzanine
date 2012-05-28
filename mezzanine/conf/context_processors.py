
from mezzanine.utils.cache import (cache_key_prefix, cache_installed,
                                   cache_get, cache_set)


def settings(request):
    """
    Add the settings object to the template context.
    """
    settings_dict = None
    if cache_installed():
        cache_key = cache_key_prefix(request) + "context-settings"
        settings_dict = cache_get(cache_key)
    if not settings_dict:
        from mezzanine.conf import settings
        settings.use_editable()
        settings_dict = dict([(k, getattr(settings, k, ""))
                              for k in settings.TEMPLATE_ACCESSIBLE_SETTINGS])
        if cache_installed():
            cache_set(cache_key, settings_dict)
    return {"settings": type("Settings", (), settings_dict)}
