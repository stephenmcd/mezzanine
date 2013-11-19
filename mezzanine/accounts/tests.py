from __future__ import unicode_literals

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.http import int_to_base36

from mezzanine.accounts import get_profile_model, get_profile_user_fieldname
from mezzanine.conf import settings
from mezzanine.utils.models import get_user_model
from mezzanine.utils.tests import TestCase


User = get_user_model()


class AccountsTests(TestCase):

    def account_data(self, test_value):
        """
        Returns a dict with test data for all the user/profile fields.
        """
        # User fields
        data = {"email": test_value + "@example.com"}
        for field in ("first_name", "last_name", "username",
                      "password1", "password2"):
            if field.startswith("password"):
                value = "x" * settings.ACCOUNTS_MIN_PASSWORD_LENGTH
            else:
                value = test_value
            data[field] = value
        # Profile fields
        Profile = get_profile_model()
        if Profile is not None:
            user_fieldname = get_profile_user_fieldname()
            for field in Profile._meta.fields:
                if field.name not in (user_fieldname, "id"):
                    if field.choices:
                        value = field.choices[0][0]
                    else:
                        value = test_value
                    data[field.name] = value
        return data

    def test_account(self):
        """
        Test account creation.
        """
        # Verification not required - test an active user is created.

        data = self.account_data("test1")
        settings.ACCOUNTS_VERIFICATION_REQUIRED = False
        response = self.client.post(reverse("signup"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(email=data["email"], is_active=True)
        self.assertEqual(len(users), 1)
        # Verification required - test an inactive user is created,
        settings.ACCOUNTS_VERIFICATION_REQUIRED = True
        data = self.account_data("test2")
        emails = len(mail.outbox)
        response = self.client.post(reverse("signup"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(email=data["email"], is_active=False)
        self.assertEqual(len(users), 1)
        # Test the verification email.
        self.assertEqual(len(mail.outbox), emails + 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], data["email"])
        # Test the verification link.
        new_user = users[0]
        verification_url = reverse("signup_verify", kwargs={
            "uidb36": int_to_base36(new_user.id),
            "token": default_token_generator.make_token(new_user),
        })
        response = self.client.get(verification_url, follow=True)
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(email=data["email"], is_active=True)
        self.assertEqual(len(users), 1)
