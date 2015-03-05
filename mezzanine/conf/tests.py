from __future__ import unicode_literals
from future.builtins import bytes, str

from django.conf import settings as django_settings
from django.utils.unittest import skipUnless

from mezzanine.conf import settings, registry, register_setting
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
            settings.use_editable()
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
            settings.use_editable()

    def test_settings(self):
        """
        Test that an editable setting can be overridden with a DB
        value and that the data type is preserved when the value is
        returned back out of the DB. Also checks to ensure no
        unsupported types are defined for editable settings.
        """
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
        settings.use_editable()
        for (name, value) in values_by_name.items():
            self.assertEqual(getattr(settings, name), value)

    def test_editable_override(self):
        """
        Test that an editable setting is always overridden by a settings.py
        setting of the same name.
        """
        Setting.objects.all().delete()
        django_settings.FOO = "Set in settings.py"
        db_value = Setting(name="FOO", value="Set in database")
        db_value.save()
        settings.use_editable()
        first_value = settings.FOO
        settings.SITE_TITLE  # Triggers access?
        second_value = settings.FOO
        self.assertEqual(first_value, second_value)

    def test_bytes_conversion(self):
        register_setting(name="BYTES_TEST_SETTING", editable=True, default=b"")
        Setting.objects.create(name="BYTES_TEST_SETTING",
                               value="A unicode value")
        settings.use_editable()
        self.assertEqual(settings.BYTES_TEST_SETTING, b"A unicode value")

    def test_modeltranslation_configuration(self):
        """
        Test that modeltranslation is properly configured in settings.
        """
        if settings.USE_MODELTRANSLATION:
            self.assertTrue(settings.USE_I18N)
