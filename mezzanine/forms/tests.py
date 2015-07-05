from __future__ import unicode_literals

from mezzanine.conf import settings
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.forms import fields
from mezzanine.forms.models import Form
from mezzanine.utils.tests import TestCase
from django.utils.unittest import skipUnless


class TestsForm(TestCase):

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

    @skipUnless(settings.USE_MODELTRANSLATION and len(settings.LANGUAGES) > 1,
                "modeltranslation configured for several languages required")
    def test_submit_button_text(self):
        """
        Test that Form.button_text has its value displayed properly without
        being translated back to the default language.
        """
        from django.core.urlresolvers import reverse
        from django.utils.translation import (get_language, activate,
                                              ugettext as _)
        from django.utils.datastructures import SortedDict
        from modeltranslation.utils import auto_populate

        default_language = get_language()
        code_list = SortedDict(settings.LANGUAGES)
        del code_list[default_language]
        for c in code_list:
            try:
                activate(c)
            except:
                pass
            else:
                break
            return
        with auto_populate(True):
            form = Form.objects.create(title="Form button_text",
                                       status=CONTENT_STATUS_PUBLISHED)
            form.fields.create(label="Field test", field_type=fields.TEXT,
                               required=True, visible=True)
        submit_text = _("Submit")
        form.button_text = submit_text
        form.save()
        # Client session still uses default language
        response = self.client.get(form.get_absolute_url())
        activate(default_language)
        # Default language contains the default translation for Submit
        self.assertContains(response, _("Submit"))
        # Language used for form creation contains its own translation
        self.client.post(reverse('set_language'), data={'language': c})
        response = self.client.get(form.get_absolute_url())
        self.client.post(reverse('set_language'), data={'language':
                                                        default_language})
        self.assertContains(response, submit_text)
