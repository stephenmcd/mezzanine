
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from mezzanine.conf import settings, registry
from mezzanine.core.managers import DisplayableManager
from mezzanine.conf.models import Setting
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.forms import fields
from mezzanine.forms.models import Form
from mezzanine.pages.models import RichTextPage
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.tests import (TestCase, run_pyflakes_for_package,
                                             run_pep8_for_package)
from mezzanine.utils.html import TagCloser


class CoreTests(TestCase):
    """
    Mezzanine tests.
    """

    def test_tagcloser(self):
        """
        Test tags are closed, and tags that shouldn't be closed aren't.
        """
        self.assertEqual(TagCloser("<p>Unclosed paragraph").html,
                         "<p>Unclosed paragraph</p>")

        self.assertEqual(TagCloser("Line break<br>").html,
                         "Line break<br>")

    def test_device_specific_template(self):
        """
        Test that an alternate template is rendered when a mobile
        device is used.
        """
        try:
            get_template("mobile/index.html")
        except TemplateDoesNotExist:
            return
        ua = settings.DEVICE_USER_AGENTS[0][1][0]
        kwargs = {"slug": "device-test"}
        url = reverse("page", kwargs=kwargs)
        kwargs["status"] = CONTENT_STATUS_PUBLISHED
        RichTextPage.objects.get_or_create(**kwargs)
        default = self.client.get(url)
        mobile = self.client.get(url, HTTP_USER_AGENT=ua)
        self.assertNotEqual(default.template_name[0], mobile.template_name[0])

    def test_forms(self):
        """
        Simple 200 status check against rendering and posting to forms
        with both optional and required fields.
        """
        for required in (True, False):
            form = Form.objects.create(title="Form",
                                       status=CONTENT_STATUS_PUBLISHED)
            for (i, (field, _)) in enumerate(fields.NAMES):
                form.fields.create(label="Field %s" % i, field_type=field,
                                   required=required, visible=True)
            response = self.client.get(form.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            visible_fields = form.fields.visible()
            data = dict([("field_%s" % f.id, "test") for f in visible_fields])
            response = self.client.post(form.get_absolute_url(), data=data)
            self.assertEqual(response.status_code, 200)

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
            elif setting_type in (str, unicode):
                setting_value += "test"
            else:
                setting = "%s: %s" % (setting_name, setting_type)
                self.fail("Unsupported setting type for %s" % setting)
            values_by_name[setting_name] = setting_value
            Setting.objects.create(name=setting_name, value=str(setting_value))
        # Load the settings and make sure the DB values have persisted.
        settings.use_editable()
        for (name, value) in values_by_name.items():
            self.assertEqual(getattr(settings, name), value)

    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        warnings = []
        warnings.extend(run_pyflakes_for_package("mezzanine"))
        warnings.extend(run_pep8_for_package("mezzanine"))
        if warnings:
            self.fail("Syntax warnings!\n\n%s" % "\n".join(warnings))

    def test_utils(self):
        """
        Miscellanous tests for the ``mezzanine.utils`` package.
        """
        self.assertRaises(ImportError, import_dotted_path, "mezzanine")
        self.assertRaises(ImportError, import_dotted_path, "mezzanine.NO")
        self.assertRaises(ImportError, import_dotted_path, "mezzanine.core.NO")
        try:
            import_dotted_path("mezzanine.core")
        except ImportError:
            self.fail("mezzanine.utils.imports.import_dotted_path"
                      "could not import \"mezzanine.core\"")

    def test_searchable_manager_search_fields(self):
        """
        Test that SearchableManager can get appropriate params.
        """
        manager = DisplayableManager()
        self.assertFalse(manager._search_fields)
        manager = DisplayableManager(search_fields={'foo': 10})
        self.assertTrue(manager._search_fields)
