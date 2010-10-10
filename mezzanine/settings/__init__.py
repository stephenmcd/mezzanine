
from mezzanine.settings import defaults
from mezzanine.settings.models import Setting


def load_settings(*names):
    """
    Returns a settings object using the given settings names as attributes. 
    Values are loaded when the first name is accessed. Settings are loaded
    from the DB for settings marked as editable, and from 
    ``mezzanine.settings.defaults`` for those not retrieved from the DB.
    """

    class Settings(object):
    
        def __getattr__(self, name):
            if name == "_loaded":
                return False
            elif getattr(self, "_loaded"):
                raise AttributeError("Setting does not exist: %s" % name)
            self._loaded = True
            editable = [n for n in names if hasattr(defaults, n) and 
                getattr(defaults, n)["editable"]]
            if editable:
                for setting in Setting.objects.filter(name__in=editable):
                    setattr(self, setting.name, setting.value)
            for n in names:
                if n not in self.__dict__ and hasattr(defaults, n):
                    setattr(self, n, getattr(defaults, n)["default"])
            return getattr(self, name)
    
    return Settings()
