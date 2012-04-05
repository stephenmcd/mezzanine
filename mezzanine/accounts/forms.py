
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.validators import validate_email, ValidationError
from django import forms
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings


class UserForm(forms.Form):
    """
    Fields for signup & login.
    """
    email = forms.EmailField(label=_("Email Address"))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))

    def __init__(self, request, *args, **kwargs):
        """
        Try and pre-populate the email field with a cookie value.
        """
        initial = {}
        for value in request.COOKIES.values():
            try:
                validate_email(value)
            except ValidationError:
                pass
            else:
                initial["email"] = value
                break
        super(UserForm, self).__init__(initial=initial, *args, **kwargs)

    def authenticate(self):
        """
        Validate email and password as well as setting the user for login.
        """
        self._user = authenticate(username=self.cleaned_data.get("email", ""),
                               password=self.cleaned_data.get("password", ""))

    def login(self, request):
        """
        Log the user in.
        """
        login(request, self._user)


class SignupForm(UserForm):

    def clean_email(self):
        """
        Ensure the email address is not already registered.
        """
        email = self.cleaned_data["email"]
        try:
            User.objects.get(username=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("This email is already registered"))

    def save(self):
        """
        Create the new user using their email address as their username.
        """
        user = User.objects.create_user(self.cleaned_data["email"],
                                        self.cleaned_data["email"],
                                        self.cleaned_data["password"])
        settings.use_editable()
        if settings.ACCOUNTS_VERIFICATION_REQUIRED:
            user.is_active = False
            user.save()
        else:
            self.authenticate()
        return user


class LoginForm(UserForm):

    def clean(self):
        """
        Authenticate the email/password.
        """
        if "email" in self.cleaned_data and "password" in self.cleaned_data:
            self.authenticate()
            if self._user is None:
                raise forms.ValidationError(_("Invalid email/password"))
            elif not self._user.is_active:
                raise forms.ValidationError(_("Your account is inactive"))
        return self.cleaned_data
