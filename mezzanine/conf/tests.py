from __future__ import unicode_literals
from future.builtins import bytes, str
import sys

from django.conf import settings as django_settings
from django.utils.unittest import skipUnless

from mezzanine.conf import settings, registry, register_setting
from mezzanine.conf.models import Setting
from mezzanine.utils.tests import TestCase


class ConfTests(TestCase):

    @skipUnless(sys.version_info[0] == 2,
                "Randomly fails or succeeds under Python 3 as noted in "
                "GH #858 - please fix.")
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
