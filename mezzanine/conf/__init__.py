
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
        self._editable_cache = {}

    def __getattr__(self, name):

        # Lookup name as a registered setting or a Django setting.
        try:
            setting = registry[name]
        except KeyError:
            from django.conf import settings
            return getattr(settings, name)

        # First access for an editable setting - load from DB into cache.
        if setting["editable"] and not self._loaded:
            try:
                for setting_obj in Setting.objects.all():
                    setting_type = registry[setting_obj.name]["type"]
                    if setting_type is bool:
                        setting_value = setting_obj.value != "False"
                    else:
                        setting_value = setting_type(setting_obj.value)
                    self._editable_cache[setting_obj.name] = setting_value
                self._loaded = True
            except DatabaseError:
                # Allows for syncdb and other commands related to DB 
                # management to get up and running without the settings 
                # table existing.
                pass

        # Use cached editable setting if found, otherwise use default.
        try:
            setting_value = self._editable_cache[name]
        except KeyError:
            pass
        else:
            return setting_value
        return setting["default"]


for app in settings.INSTALLED_APPS:
    try:
        __import__("%s.defaults" % app)
    except ImportError:
        pass
        
settings = Settings()
