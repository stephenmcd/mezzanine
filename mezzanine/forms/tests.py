
from django.contrib.auth.models import User
from django.test import TestCase

from forms_builder.forms.models import Form, FIELD_CHOICES, \
    STATUS_DRAFT, STATUS_PUBLISHED


class Tests(TestCase):

    def test_form_fields(self):
        """
        Simple 200 status check against rendering and posting to forms with 
        both optional and required fields.
        """
        for required in (True, False):
            form = Form.objects.create(title="Test", status=STATUS_PUBLISHED)
            for field in FIELD_CHOICES:
                form.fields.create(label=field[0], field_type=field[0], 
                    required=required, visible=True)
            response = self.client.get(form.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            fields = form.fields.visible()
            data = dict([("field_%s" % f.id, "test") for f in fields])
            response = self.client.post(form.get_absolute_url(), data=data)
            self.assertEqual(response.status_code, 200)

    def test_draft_form(self):
        """
        Test that a form with draft status is only visible to staff.
        """
        username = "test"
        password = "test"
        User.objects.create_superuser(username, "", password)
        self.client.logout()
        draft = Form.objects.create(title="Draft", status=STATUS_DRAFT)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        self.client.login(username=username, password=password)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 200)

