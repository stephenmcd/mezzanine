"""
Drop-in replacement for ``django.conf.settings`` that provides a
consistent access method for settings defined in applications, the project
or Django itself. Settings can also be made editable via the admin.
"""

from django.conf import settings as django_settings
from django.utils.encoding import force_unicode
from django.utils.functional import Promise

from mezzanine import __version__


registry = {}


def register_setting(name="", label="", editable=False, description="",
                     default=None, choices=None, append=False):
    """
    Registers a setting that can be edited via the admin.
    """
    # Check project's settings module for overridden default.
    if append and name in registry:
        registry[name]["default"] += default
    else:
        default = getattr(django_settings, name, default)
        if isinstance(default, Promise):
            default = force_unicode(default)
        setting_type = type(default)
        if not label:
            label = name.replace("_", " ").title()
        if setting_type is str:
            setting_type = unicode
        registry[name] = {"name": name, "label": label,
                          "description": description,
                          "editable": editable, "default": default,
                          "choices": choices, "type": setting_type}


class Settings(object):
    """
    An object that provides settings via dynamic attribute access.
    Settings that are registered as editable and can therefore be
    stored in the database are *all* loaded once only, the first
    time *any* editable setting is accessed. When accessing uneditable
    settings their default values are used. The Settings object also
    provides access to Django settings via ``django.conf.settings`` in
    order to provide a consistent method of access for all settings.
    """

    def __init__(self):
        """
        Marking loaded as ``True`` to begin with prevents some nasty
        errors when the DB table is first created.
        """
        self._loaded = True
        self._editable_cache = {}

    def use_editable(self):
        """
        Empty the editable settings cache and set the loaded flag to
        ``False`` so that settings will be loaded from the DB on next
        access. If the conf app is not installed then set the loaded
        flag to ``True`` in order to bypass DB lookup entirely.
        """
        self._loaded = __name__ not in getattr(self, "INSTALLED_APPS")
        self._editable_cache = {}

    def __getattr__(self, name):

        # Lookup name as a registered setting or a Django setting.
        try:
            setting = registry[name]
        except KeyError:
            return getattr(django_settings, name)

        # First access for an editable setting - load from DB into cache.
        # Also remove settings from the DB that are no longer registered.
        if setting["editable"] and not self._loaded:
            from mezzanine.conf.models import Setting
            settings = Setting.objects.all()
            removed = []
            for setting_obj in settings:
                try:
                    setting_type = registry[setting_obj.name]["type"]
                except KeyError:
                    removed.append(setting_obj.id)
                else:
                    if setting_type is bool:
                        setting_value = setting_obj.value != "False"
                    else:
                        setting_value = setting_type(setting_obj.value)
                    self._editable_cache[setting_obj.name] = setting_value
            if removed:
                Setting.objects.filter(id__in=removed).delete()
            self._loaded = True

        # Use cached editable setting if found, otherwise use default.
        try:
            return self._editable_cache[name]
        except KeyError:
            return setting["default"]


mezz_first = lambda app: not app.startswith("mezzanine.")
for app in sorted(django_settings.INSTALLED_APPS, key=mezz_first):
    try:
        __import__("%s.defaults" % app)
    except (ImportError, ValueError):  # ValueError raised by convert_to_south
        pass

settings = Settings()
