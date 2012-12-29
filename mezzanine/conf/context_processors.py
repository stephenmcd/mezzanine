
from mezzanine.utils.cache import (cache_key_prefix, cache_installed,
                                   cache_get, cache_set)


# Deprecated settings and their defaults.
DEPRECATED = {
    "PAGES_MENU_SHOW_ALL": True
}


class TemplateSettings(dict):
    """
    Dict wrapper for template settings. This exists only to warn when
    deprecated settings are accessed in templates.
    """

    def __getitem__(self, k):
        if k in DEPRECATED:
            from warnings import warn
            warn("%s is deprecated, please remove it from your templates" % k)
        return super(TemplateSettings, self).__getitem__(k)

    def __getattr__(self, name):
        try:
            self.__getitem__(name)
        except KeyError:
            raise AttributeError


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
        settings_dict = TemplateSettings()
        for k in settings.TEMPLATE_ACCESSIBLE_SETTINGS:
            settings_dict[k] = getattr(settings, k, "")
        for k in DEPRECATED:
            settings_dict[k] = getattr(settings, k, DEPRECATED)
        if cache_installed():
            cache_set(cache_key, settings_dict)
    return {"settings": settings_dict}
