"""
Drop-in replacement for ``django.conf.settings`` that provides a
consistent access method for settings defined in applications, the project
or Django itself. Settings can also be made editable via the admin.
"""

from __future__ import unicode_literals
from warnings import warn
from future.builtins import bytes, int, str

from django.conf import settings as django_settings
try:
    from django.utils.encoding import force_text
except ImportError:
    # Backward compatibility for Py2 and Django < 1.5
    from django.utils.encoding import force_unicode as force_text
from django.utils.functional import Promise
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from mezzanine import __version__


registry = {}


def register_setting(name="", label="", editable=False, description="",
                     default=None, choices=None, append=False):
    """
    Registers a setting that can be edited via the admin.
    """
    # append is True when called from an app (typically external)
    # after the setting has already been registered, with the
    # intention of appending to its default value.
    if append and name in registry:
        registry[name]["default"] += default
    else:
        # If an editable setting has a value defined in the
        # project's settings.py module, it can't be editable, since
        # these lead to a lot of confusion once its value gets
        # defined in the db.
        if hasattr(django_settings, name):
            editable = False
        if isinstance(default, Promise):
            default = force_text(default)
        if not label:
            label = name.replace("_", " ").title()
        # The next six lines are for Python 2/3 compatibility.
        # isinstance() is overridden by future on Python 2 to behave as
        # on Python 3 in conjunction with either Python 2's native types
        # or the future.builtins types.
        if isinstance(default, int):        # an int or long or subclass on Py2
            setting_type = int
        elif isinstance(default, str):      # a unicode or subclass on Py2
            setting_type = str
        elif isinstance(default, bytes):    # a byte-string or subclass on Py2
            setting_type = bytes
        else:
            setting_type = type(default)
        registry[name] = {"name": name, "label": label,
                          "description": description,
                          "editable": editable, "default": default,
                          "choices": choices, "type": setting_type}


class Settings(object):
    """
    An object that provides settings via dynamic attribute access.

    Settings that are registered as editable will be stored in the
    database once the site settings form in the admin is first saved.
    When these values are accessed via this settings object, *all*
    database stored settings get retrieved from the database.

    When accessing uneditable settings their default values are used,
    unless they've been given a value in the project's settings.py
    module.

    The settings object also provides access to Django settings via
    ``django.conf.settings``, in order to provide a consistent method
    of access for all settings.
    """

    def __init__(self):
        """
        The ``_loaded`` attribute is a flag for defining whether
        editable settings have been loaded from the database. It
        defaults to ``True`` here to avoid errors when the DB table
        is first created. It's then set to ``False`` whenever the
        ``use_editable`` method is called, which should be called
        before using editable settings in the database.
        ``_editable_cache`` is the dict that stores the editable
        settings once they're loaded from the database, the first
        time an editable setting is accessed.
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

    def _load(self):
        """
        Load settings from the database into cache. Delete any settings from
        the database that are no longer registered, and emit a warning if
        there are settings that are defined in settings.py and the database.
        """
        from mezzanine.conf.models import Setting
        db_settings = {s.name: s for s in Setting.objects.all()}

        removed_settings = [s for s in db_settings if s not in registry]
        if removed_settings:
            Setting.objects.filter(name__in=removed_settings).delete()
            for s in removed_settings:
                del db_settings[s]

        conflicting_settings = [
            s for s in db_settings
            if hasattr(django_settings, s)
            and db_settings[s] != registry[s]["default"]]
        if conflicting_settings:
            warn("These settings are defined in both settings.py and "
                 "the database: %s. The settings.py values will be used."
                 % ", ".join(conflicting_settings))

        editable_settings = [s for s in db_settings if registry[s]['editable']]
        for s in editable_settings:
            setting_obj = db_settings[s]
            setting_type = registry[setting_obj.name]["type"]
            if setting_type is bool:
                setting_value = setting_obj.value != "False"
            else:
                try:
                    setting_value = setting_type(setting_obj.value)
                except ValueError:
                    # Shouldn't occur, but just a safeguard
                    # for if the db value somehow ended up as
                    # an invalid type.
                    default = registry[setting_obj.name]["default"]
                    setting_value = default
            self._editable_cache[setting_obj.name] = setting_value
        self._loaded = True

    def __getattr__(self, name):

        # Lookup name as a registered setting or a Django setting.
        try:
            setting = registry[name]
        except KeyError:
            return getattr(django_settings, name)

        # First access for an editable setting - load from DB into cache.
        if setting["editable"] and not self._loaded:
            self._load()

        # Use cached editable setting if found, otherwise use the
        # value defined in the project's settings.py module if it
        # exists, finally falling back to the default defined when
        # registered.
        try:
            return self._editable_cache[name]
        except KeyError:
            return getattr(django_settings, name, setting["default"])


mezz_first = lambda app: not app.startswith("mezzanine.")
for app in sorted(django_settings.INSTALLED_APPS, key=mezz_first):
    module = import_module(app)
    try:
        import_module("%s.defaults" % app)
    except:
        if module_has_submodule(module, "defaults"):
            raise

settings = Settings()
