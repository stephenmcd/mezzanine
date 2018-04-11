from __future__ import unicode_literals
from future.builtins import bytes, str

from unittest import skipUnless
import warnings

from django.conf import settings as django_settings
from django.utils.encoding import force_text

from mezzanine.conf import settings, registry, register_setting
from mezzanine.conf.context_processors import TemplateSettings
from mezzanine.conf.models import Setting
from mezzanine.utils.tests import TestCase


class ConfTests(TestCase):

    @skipUnless(False, "Only run manually - see Github issue #1126")
    def test_threading_race(self):
        import multiprocessing.pool
        import random
        from django.db import connections

        type_modifiers = {int: lambda s: s + 1,
                          float: lambda s: s + 1.0,
                          bool: lambda s: not s,
                          str: lambda s: s + u"test",
                          bytes: lambda s: s + b"test"}

        # Store a non-default value for every editable setting in the database
        editable_settings = {}
        for setting in registry.values():
            if setting["editable"]:
                modified = type_modifiers[setting["type"]](setting["default"])
                Setting.objects.create(name=setting["name"], value=modified)
                editable_settings[setting["name"]] = modified

        # Make our child threads use this thread's connections. Recent SQLite
        # do support access from multiple threads for in-memory databases, but
        # Django doesn't support it currently - so we have to resort to this
        # workaround, taken from Django's LiveServerTestCase.
        # See Django ticket #12118 for discussion.
        connections_override = {}
        for conn in connections.all():
            # If using in-memory sqlite databases, pass the connections to
            # the server thread.
            if (conn.vendor == 'sqlite' and
                    conn.settings_dict['NAME'] == ':memory:'):
                # Explicitly enable thread-shareability for this connection
                conn._old_allow_thread_sharing = conn.allow_thread_sharing
                conn.allow_thread_sharing = True
                connections_override[conn.alias] = conn

        def initialise_thread():
            for alias, connection in connections_override.items():
                connections[alias] = connection

        thread_pool = multiprocessing.pool.ThreadPool(8, initialise_thread)

        def retrieve_setting(setting_name):
            return setting_name, getattr(settings, setting_name)

        def choose_random_setting(length=5000):
            choices = list(editable_settings)
            for _ in range(length):
                yield random.choice(choices)

        try:
            for setting in thread_pool.imap_unordered(retrieve_setting,
                                                      choose_random_setting()):
                name, retrieved_value = setting
                self.assertEqual(retrieved_value, editable_settings[name])
        finally:
            for conn in connections_override.values():
                conn.allow_thread_sharing = conn._old_allow_thread_sharing
                del conn._old_allow_thread_sharing
            Setting.objects.all().delete()

    def test_settings(self):
        """
        Test that an editable setting can be overridden with a DB
        value and that the data type is preserved when the value is
        returned back out of the DB. Also checks to ensure no
        unsupported types are defined for editable settings.
        """

        settings.clear_cache()

        # Find an editable setting for each supported type.
        names_by_type = {}
        for setting in registry.values():
            if setting["editable"] and setting["type"] not in names_by_type:
                names_by_type[setting["type"]] = setting["name"]
        # Create a modified value for each setting and save it.
        values_by_name = {}
        for (setting_type, setting_name) in names_by_type.items():
            setting_value = registry[setting_name]["default"]
            if setting_type in (int, float):
                setting_value += 1
            elif setting_type is bool:
                setting_value = not setting_value
            elif setting_type is str:
                setting_value += u"test"
            elif setting_type is bytes:
                setting_value += b"test"
            else:
                setting = "%s: %s" % (setting_name, setting_type)
                self.fail("Unsupported setting type for %s" % setting)
            values_by_name[setting_name] = setting_value
            Setting.objects.create(name=setting_name, value=setting_value)
        # Load the settings and make sure the DB values have persisted.
        for (name, value) in values_by_name.items():
            self.assertEqual(getattr(settings, name), value)

    def test_editable_override(self):
        """
        Test that an editable setting is always overridden by a settings.py
        setting of the same name.
        """

        settings.clear_cache()

        Setting.objects.all().delete()
        django_settings.FOO = "Set in settings.py"
        Setting.objects.create(name="FOO", value="Set in database")
        first_value = settings.FOO
        settings.SITE_TITLE  # Triggers access?
        second_value = settings.FOO
        self.assertEqual(first_value, second_value)

    def test_bytes_conversion(self):

        settings.clear_cache()

        register_setting(name="BYTES_TEST_SETTING", editable=True, default=b"")
        Setting.objects.create(name="BYTES_TEST_SETTING",
                               value="A unicode value")
        self.assertEqual(settings.BYTES_TEST_SETTING, b"A unicode value")

    def test_invalid_value_warning(self):
        """
        Test that a warning is raised when a database setting has an invalid
        value, i.e. one that can't be converted to the correct Python type.
        """

        settings.clear_cache()

        register_setting(name="INVALID_INT_SETTING", editable=True, default=0)
        Setting.objects.create(name="INVALID_INT_SETTING", value='zero')
        with warnings.catch_warnings():
            warning_re = r'The setting \w+ should be of type'
            warnings.filterwarnings('error', warning_re, UserWarning)
            with self.assertRaises(UserWarning):
                settings.INVALID_INT_SETTING
        self.assertEqual(settings.INVALID_INT_SETTING, 0)

    def test_unregistered_setting(self):
        """
        Test that accessing any editable setting will delete all Settings
        with no corresponding registered setting from the database.
        """

        settings.clear_cache()

        register_setting(name="REGISTERED_SETTING", editable=True, default="")
        Setting.objects.create(name="UNREGISTERED_SETTING", value='')

        with self.assertRaises(AttributeError):
            settings.UNREGISTERED_SETTING

        qs = Setting.objects.filter(name="UNREGISTERED_SETTING")
        self.assertEqual(qs.count(), 1)

        # This triggers Settings._load(), which deletes unregistered Settings
        settings.REGISTERED_SETTING

        self.assertEqual(qs.count(), 0)

    def test_conflicting_setting(self):
        """
        Test that conflicting settings raise a warning and use the settings.py
        value instead of the value from the database.
        """

        settings.clear_cache()

        register_setting(name="CONFLICTING_SETTING", editable=True, default=1)
        Setting.objects.create(name="CONFLICTING_SETTING", value=2)
        settings.CONFLICTING_SETTING = 3

        with warnings.catch_warnings():
            warning_re = ("These settings are defined in both "
                          "settings\.py and the database")
            warnings.filterwarnings('error', warning_re, UserWarning)

            with self.assertRaises(UserWarning):
                settings.CONFLICTING_SETTING

        self.assertEqual(settings.CONFLICTING_SETTING, 3)

        del settings.CONFLICTING_SETTING

    def test_modeltranslation_configuration(self):
        """
        Test that modeltranslation is properly configured in settings.
        """
        if settings.USE_MODELTRANSLATION:
            self.assertTrue(settings.USE_I18N)

    def test_editable_caching(self):
        """
        Test the editable setting caching behavior.
        """

        # Ensure usage with no current request does not break caching
        from mezzanine.core.request import _thread_local
        try:
            del _thread_local.request
        except AttributeError:
            pass

        setting = Setting.objects.create(name='SITE_TITLE', value="Mezzanine")
        original_site_title = settings.SITE_TITLE
        setting.value = "Foobar"
        setting.save()
        new_site_title = settings.SITE_TITLE
        setting.delete()
        self.assertNotEqual(original_site_title, new_site_title)


class TemplateSettingsTests(TestCase):
    def test_allowed(self):
        # We choose a setting that will definitely exist:
        ts = TemplateSettings(settings, ['INSTALLED_APPS'])
        self.assertEqual(ts.INSTALLED_APPS, settings.INSTALLED_APPS)
        self.assertEqual(ts['INSTALLED_APPS'], settings.INSTALLED_APPS)

    def test_not_allowed(self):
        ts = TemplateSettings(settings, [])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertRaises(AttributeError, lambda: ts.INSTALLED_APPS)
            self.assertRaises(KeyError, lambda: ts['INSTALLED_APPS'])

    def test_add(self):
        ts = TemplateSettings(settings, ['INSTALLED_APPS'])
        ts['EXTRA_THING'] = 'foo'
        self.assertEqual(ts.EXTRA_THING, 'foo')
        self.assertEqual(ts['EXTRA_THING'], 'foo')

    def test_repr(self):
        ts = TemplateSettings(settings, [])
        self.assertEqual(repr(ts), '{}')

        ts2 = TemplateSettings(settings,
                               ['DEBUG', 'SOME_NON_EXISTANT_SETTING'])
        self.assertIn("'DEBUG': False", repr(ts2))

        ts3 = TemplateSettings(settings, [])
        ts3['EXTRA_THING'] = 'foo'
        self.assertIn("'EXTRA_THING'", repr(ts3))
        self.assertIn("'foo'", repr(ts3))

    def test_force_text(self):
        ts = TemplateSettings(settings, [])
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(force_text(ts), '{}')
        self.assertEqual(len(w), 0)
