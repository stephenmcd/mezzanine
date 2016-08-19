from __future__ import unicode_literals

from warnings import warn


# Deprecated settings and their defaults.
DEPRECATED = {}


class TemplateSettings(dict):
    """
    Dict wrapper for template settings. This exists to enforce
    the restriction of settings in templates to those named in
    TEMPLATE_ACCESSIBLE_SETTINGS, and to warn about deprecated settings.

    Django's template system attempts a dict-style index lookup before an
    attribute lookup when resolving dot notation in template variables, so we
    use ``__getitem__()`` this as the primary way of getting at the settings.
    """

    def __init__(self, settings, allowed_settings, *args, **kwargs):
        super(TemplateSettings, self).__init__(*args, **kwargs)
        self.settings = settings
        self.allowed_settings = set(allowed_settings)

    def __getattr__(self, k):
        try:
            return self.__getitem__(k)
        except KeyError:
            raise AttributeError

    def __getitem__(self, k):

        if k not in self.allowed_settings:
            warn("%s is not in TEMPLATE_ACCESSIBLE_SETTINGS." % k)
            raise KeyError

        if k in DEPRECATED:
            warn("%s is deprecated. Please remove it from your templates." % k)

        try:
            return getattr(self.settings, k)
        except AttributeError:
            return super(TemplateSettings, self).__getitem__(k)

    def __setitem__(self, k, v):
        self.allowed_settings.add(k)
        super(TemplateSettings, self).__setitem__(k, v)


def settings(request=None):
    """
    Add the settings object to the template context.
    """
    from mezzanine.conf import settings

    allowed_settings = settings.TEMPLATE_ACCESSIBLE_SETTINGS

    template_settings = TemplateSettings(settings, allowed_settings)
    template_settings.update(DEPRECATED)

    # This is basically the same as the old ADMIN_MEDIA_PREFIX setting,
    # we just use it in a few spots in the admin to optionally load a
    # file from either grappelli or Django admin if grappelli isn't
    # installed. We don't call it ADMIN_MEDIA_PREFIX in order to avoid
    # any confusion.
    admin_prefix = "grappelli/" if settings.GRAPPELLI_INSTALLED else "admin/"
    template_settings["MEZZANINE_ADMIN_PREFIX"] = admin_prefix

    return {"settings": template_settings}
