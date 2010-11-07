
from django.conf import settings
from django.db import DatabaseError

from mezzanine.conf.models import Setting


registry = {}


def register_setting(name="", editable=False, description="", default=None):
    """
    Registers a setting that can be edited via the admin.
    """
    default = getattr(settings, "MEZZANINE_%s" % name, default)
    registry[name] = {"name": name, "description": description, "editable":
        editable, "default": default, "type": type(default)}


def editable_settings(names=None):
    """
    Returns the names of editable settings.
    """
    if names is None:
        names = registry.keys()
    return [k for (k, v) in registry.items() if v["editable"] and k in names]


class Settings(object):
    """
    An object that provides settings via dynamic attribute access. Settings 
    that are registered as editable and can therefore be stored in the 
    database are *all* loaded once only, the first time *any* editable 
    setting is accessed. When accessing uneditable settings their default 
    values are used. The Settings object also provides access to Django 
    settings via django.conf.settings in order to provide a consistent 
    method of access for all settings.
    """

    def __init__(self):
        self.use_editable()
    
    def use_editable(self):
        """
        Set the loaded flag to False if editable settings are enabled so that 
        settings will be loaded from the DB on next access.
        """
        self._loaded = not registry["SETTINGS_EDITABLE"]["default"]

    def __getattr__(self, name):
        try:
            setting = registry[name]
        except KeyError:
            # Try django.conf.settings if requested name isn't registered.
            from django.conf import settings
            try:
                setting = getattr(settings, name)
            except AttributeError:
                raise AttributeError("Setting does not exist: %s" % name)
            return setting
        if self._loaded or not setting["editable"]:
            return setting["default"]
        # First time an editable setting is requested - load from DB.
        try:
            for setting in Setting.objects.all():
                setting_type = registry[setting.name]["type"]
                if setting_type is bool:
                    setting_value = setting.value != "False"
                else:
                    setting_value = setting_type(setting.value)
                setattr(self, setting.name, setting_value)
            self._loaded = True
            return getattr(self, name)
        except DatabaseError:
            # Allows for syncdb and other commands related to DB 
            # management to get up and running without the settings 
            # table existing.
            return setting["default"]


for app in settings.INSTALLED_APPS:
    try:
        __import__("%s.defaults" % app)
    except ImportError:
        pass
        
settings = Settings()
