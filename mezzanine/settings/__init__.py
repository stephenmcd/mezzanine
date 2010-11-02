
import sys

from django.conf import settings

from mezzanine.settings.models import Setting


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


def load_settings(*names):
    """
    Returns a settings object using the given settings names as attributes. 
    Values are loaded when the first name is accessed. Settings are loaded
    from the DB for settings marked as editable, and from 
    ``mezzanine.settings.registry`` for those not retrieved from the DB.
    """

    class Settings(object):
        
        def __init__(self):
            self._loaded = False
    
        def __getattr__(self, name):
            if self._loaded:
                raise AttributeError("Setting does not exist: %s" % name)
            self._loaded = True
            editable = editable_settings(names)
            syncdb = len(sys.argv) >= 2 and sys.argv[1] == "syncdb"
            if editable and not syncdb:
                for setting in Setting.objects.filter(name__in=editable):
                    setting_type = registry[setting.name]["type"]
                    if setting_type is bool:
                        setting_value = setting.value != "False"
                    else:
                        setting_value = setting_type(setting.value)
                    setattr(self, setting.name, setting_value)
            for n in names:
                if n not in self.__dict__ and n in registry.keys():
                    setattr(self, n, registry[n]["default"])
            return getattr(self, name)

    return Settings()


for app in settings.INSTALLED_APPS:
    try:
        __import__("%s.defaults" % app)
    except ImportError:
        pass
