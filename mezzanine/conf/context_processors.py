from __future__ import unicode_literals
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
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError


def settings(request=None):
    """
    Add the settings object to the template context.
    """
    from mezzanine.conf import settings
    settings_dict = None
    cache_settings = request and cache_installed()
    if cache_settings:
        cache_key = cache_key_prefix(request) + "context-settings"
        settings_dict = cache_get(cache_key)
    if not settings_dict:
        settings.use_editable()
        settings_dict = TemplateSettings()
        for k in settings.TEMPLATE_ACCESSIBLE_SETTINGS:
            settings_dict[k] = getattr(settings, k, "")
        for k in DEPRECATED:
            settings_dict[k] = getattr(settings, k, DEPRECATED)
        if cache_settings:
            cache_set(cache_key, settings_dict)
    # This is basically the same as the old ADMIN_MEDIA_PREFIX setting,
    # we just use it in a few spots in the admin to optionally load a
    # file from either grappelli or Django admin if grappelli isn't
    # installed. We don't call it ADMIN_MEDIA_PREFIX in order to avoid
    # any confusion.
    if settings.GRAPPELLI_INSTALLED:
        settings_dict["MEZZANINE_ADMIN_PREFIX"] = "grappelli/"
    else:
        settings_dict["MEZZANINE_ADMIN_PREFIX"] = "admin/"
    return {"settings": settings_dict}
