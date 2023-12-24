from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.forms.fields import DateField, DateTimeField
from django.urls import reverse
from django.utils.http import int_to_base36

from mezzanine.accounts import ProfileNotConfigured
from mezzanine.accounts.forms import ProfileForm, PasswordResetForm
from mezzanine.conf import settings
from mezzanine.utils.tests import TestCase

User = get_user_model()


class AccountsTests(TestCase):
    def account_data(self, test_value):
        """
        Returns a dict with test data for all the user/profile fields.
        """
        # User fields
        data = {"email": test_value + "@example.com"}
        for field in ("first_name", "last_name", "username", "password1", "password2"):
            if field.startswith("password"):
                value = "x" * settings.ACCOUNTS_MIN_PASSWORD_LENGTH
            else:
                value = test_value
            data[field] = value
        # Profile fields
        try:
            profile_form = ProfileForm()
            ProfileFieldsForm = profile_form.get_profile_fields_form()
            for name, field in ProfileFieldsForm().fields.items():
                if name != "id":
                    if hasattr(field, "choices"):
                        value = list(field.choices)[0][0]
                    elif isinstance(field, (DateField, DateTimeField)):
                        value = "9001-04-20"
                    else:
                        value = test_value
                    data[name] = value
        except ProfileNotConfigured:
            pass
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
        verification_url = reverse(
            "signup_verify",
            kwargs={
                "uidb36": int_to_base36(new_user.id),
                "token": default_token_generator.make_token(new_user),
            },
        )
        response = self.client.get(verification_url, follow=True)
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(email=data["email"], is_active=True)
        self.assertEqual(len(users), 1)

        self.client.logout()

        # Create another account with the same user name
        settings.ACCOUNTS_VERIFICATION_REQUIRED = False
        data = self.account_data("test1")
        form = ProfileForm(data=data)
        self.assertFormError(form, 'username', 'This username is already registered')

        # Create another account with the same user name, but case is different
        data['username'] = 'TEST1'
        form = ProfileForm(data=data)
        self.assertFormError(form, 'username', 'This username is already registered')

        # Create another account with a different username, but same email
        data['username'] = 'test3'
        form = ProfileForm(data=data)
        self.assertFormError(form, 'email', 'This email is already registered')

        # Create another account with a different username, but same email with different case
        data['email'] = 'Test1@EXAMPLE.com'
        form = ProfileForm(data=data)
        self.assertFormError(form, 'email', 'This email is already registered')


    def test_account_login(self):
        """
        Test account login
        """
        # Create test user account
        data = self.account_data("test1")
        settings.ACCOUNTS_VERIFICATION_REQUIRED = False
        response = self.client.post(reverse("signup"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Find the valid user
        users = User.objects.filter(email=data["email"], is_active=True)
        self.assertEqual(len(users), 1)
        test_user = users[0]

        self.client.logout()

        # Log in with username/password
        self.assertTrue(self.client.login(username=data['username'],
                                          password=data['password1']))
        user = get_user(self.client)
        self.assertEqual(user, test_user)
        self.assertTrue(user.is_authenticated)
        self.client.logout()

        # Log in with email/password
        self.assertTrue(self.client.login(username=data['email'],
                                          password=data['password1']))
        user = get_user(self.client)
        self.assertEqual(user, test_user)
        self.assertTrue(user.is_authenticated)
        self.client.logout()

        # Log in with bad password
        self.assertFalse(self.client.login(username=data['username'],
                                           password=data['password1'] + 'badbit'))
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.client.logout()

        # Log in with username (different case) and password
        self.assertTrue(self.client.login(username=data['username'].upper(),
                                          password=data['password1']))
        user = get_user(self.client)
        self.assertEqual(user, test_user)
        self.assertTrue(user.is_authenticated)
        self.client.logout()

        # Log in with email (different case)  and password
        self.assertTrue(self.client.login(username=data['email'].upper(),
                                          password=data['password1']))
        user = get_user(self.client)
        self.assertEqual(user, test_user)
        self.assertTrue(user.is_authenticated)
        self.client.logout()

    def _verify_password_reset_email(self, new_user, num_emails):
        # Check email was sent
        self.assertEqual(len(mail.outbox), num_emails + 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], new_user.email)
        verification_url = reverse(
            "password_reset_verify",
            kwargs={
                "uidb36": int_to_base36(new_user.id),
                "token": default_token_generator.make_token(new_user),
            },
        )
        response = self.client.get(verification_url, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_account_password_reset(self):
        """
        Test account password reset verification email
        """
        # Create test user account
        data = self.account_data("test1")
        settings.ACCOUNTS_VERIFICATION_REQUIRED = False
        response = self.client.post(reverse("signup"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Find the valid user
        users = User.objects.filter(email=data["email"], is_active=True)
        self.assertEqual(len(users), 1)
        new_user = users[0]
        self.client.logout()

        # Reset password with username
        emails = len(mail.outbox)
        rdata = {'username': data['username']}
        response = self.client.post(reverse("mezzanine_password_reset"), rdata, follow=True)
        self.assertEqual(response.status_code, 200)
        self._verify_password_reset_email(new_user, emails)
        self.client.logout()

        # Reset password with email
        emails = len(mail.outbox)
        rdata = {'username': data['email']}
        response = self.client.post(reverse("mezzanine_password_reset"), rdata, follow=True)
        self.assertEqual(response.status_code, 200)
        self._verify_password_reset_email(new_user, emails)
        self.client.logout()

        # Reset password with username (different case)
        emails = len(mail.outbox)
        rdata = {'username': data['username'].upper()}
        response = self.client.post(reverse("mezzanine_password_reset"), rdata, follow=True)
        self.assertEqual(response.status_code, 200)
        self._verify_password_reset_email(new_user, emails)
        self.client.logout()

        # Reset password with email (different case)
        emails = len(mail.outbox)
        rdata = {'username': data['email'].upper()}
        response = self.client.post(reverse("mezzanine_password_reset"), rdata, follow=True)
        self.assertEqual(response.status_code, 200)
        self._verify_password_reset_email(new_user, emails)
        self.client.logout()

        # Reset password with invalid username
        rdata = {'username': 'badusername'}
        form = PasswordResetForm(data=rdata)
        self.assertFormError(form, None, 'Invalid username/email')

        # Reset password with invalid email
        rdata = {'username': 'badusername@example.com'}
        form = PasswordResetForm(data=rdata)
        self.assertFormError(form, None, 'Invalid username/email')
