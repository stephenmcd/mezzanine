
from django.conf import settings


registry = {}


def register_setting(name="", editable=False, description="", default=None):
    """
    Registers a setting that can be edited via the admin.
    """
    # Check project's settings module for overriden default.
    default = getattr(settings, name, default)
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
        """
        Marking loaded as True to begin with prevents some nasty errors 
        when the DB table is first created.
        """
        self._loaded = True
        self._editable_cache = {}
    
    def use_editable(self):
        """
        Empty the editable settings cache and set the loaded flag to False 
        so that settings will be loaded from the DB on next access. If the 
        conf app is not installed then set the loaded flag to True in order 
        to bypass DB lookup entirely.
        """
        self._loaded = __name__ not in getattr(self, "INSTALLED_APPS")
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
            from mezzanine.conf.models import Setting
            for setting_obj in Setting.objects.all():
                setting_type = registry[setting_obj.name]["type"]
                if setting_type is bool:
                    setting_value = setting_obj.value != "False"
                else:
                    setting_value = setting_type(setting_obj.value)
                self._editable_cache[setting_obj.name] = setting_value

        # Use cached editable setting if found, otherwise use default.
        try:
            setting_value = self._editable_cache[name]
        except KeyError:
            pass
        else:
            return setting_value
        return setting["default"]


for app in [__name__] + [a for a in settings.INSTALLED_APPS if a != __name__]:
    try:
        __import__("%s.defaults" % app)
    except ImportError:
        pass
        
settings = Settings()
