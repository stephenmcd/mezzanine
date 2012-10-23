
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django import forms
from django.utils.translation import ugettext_lazy as _

from mezzanine.accounts import get_profile_model, get_profile_user_fieldname
from mezzanine.conf import settings
from mezzanine.core.forms import Html5Mixin
from mezzanine.utils.urls import slugify


class LoginForm(Html5Mixin, forms.Form):
    """
    Fields for login.
    """
    username = forms.CharField(label=_("Username or email address"))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))

    def clean(self):
        """
        Authenticate the given username/email and password. If the fields
        are valid, store the authenticated user for returning via save().
        """
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        self._user = authenticate(username=username, password=password)
        if self._user is None:
            raise forms.ValidationError(
                             _("Invalid username/email and password"))
        elif not self._user.is_active:
            raise forms.ValidationError(_("Your account is inactive"))
        return self.cleaned_data

    def save(self):
        """
        Just return the authenticated user - used for logging in.
        """
        return getattr(self, "_user", None)


# If a profile model has been configured with the ``AUTH_PROFILE_MODULE``
# setting, create a model form for it that will have its fields added to
# ``ProfileForm``.
Profile = get_profile_model()
_exclude_fields = tuple(settings.ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS)
if Profile is not None:
    class ProfileFieldsForm(forms.ModelForm):
        class Meta:
            model = Profile
            exclude = (get_profile_user_fieldname(),) + _exclude_fields


class ProfileForm(Html5Mixin, forms.ModelForm):
    """
    ModelForm for auth.User - used for signup and profile update.
    If a Profile model is defined via ``AUTH_PROFILE_MODULE``, its
    fields are injected into the form.
    """

    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("Password (again)"),
                                widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")
        exclude = _exclude_fields

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self._signup = self.instance.id is None
        user_fields = User._meta.get_all_field_names()
        self.fields["username"].help_text = _(
                        "Only letters, numbers, dashes or underscores please")
        for field in self.fields:
            # Make user fields required.
            if field in user_fields:
                self.fields[field].required = True
            # Disable auto-complete for password fields.
            # Password isn't required for profile update.
            if field.startswith("password"):
                self.fields[field].widget.attrs["autocomplete"] = "off"
                self.fields[field].widget.attrs.pop("required", "")
                if not self._signup:
                    self.fields[field].required = False
                    if field == "password1":
                        self.fields[field].help_text = _(
                        "Leave blank unless you want to change your password")
        # Add any profile fields to the form.
        self._has_profile = Profile is not None
        if self._has_profile:
            profile_fields = ProfileFieldsForm().fields
            self.fields.update(profile_fields)
            if not self._signup:
                for field in profile_fields:
                    value = getattr(self.instance.get_profile(), field)
                    self.initial[field] = value

    def clean_username(self):
        """
        Ensure the username doesn't exist or contain invalid chars.
        We limit it to slugifiable chars since it's used as the slug
        for the user's profile view.
        """
        username = self.cleaned_data.get("username")
        if username.lower() != slugify(username).lower():
            raise forms.ValidationError(_("Username can only contain letters, "
                                          "numbers, dashes or underscores."))
        try:
            User.objects.exclude(id=self.instance.id).get(
                username__iexact=username
            )
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("This username is already registered"))

    def clean_password2(self):
        """
        Ensure the password fields are equal, and match the minimum
        length defined by ``ACCOUNTS_MIN_PASSWORD_LENGTH``.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1:
            errors = []
            if password1 != password2:
                errors.append(_("Passwords do not match"))
            if len(password1) < settings.ACCOUNTS_MIN_PASSWORD_LENGTH:
                errors.append(_("Password must be at least %s characters" %
                              settings.ACCOUNTS_MIN_PASSWORD_LENGTH))
            if errors:
                self._errors["password1"] = self.error_class(errors)
        return password2

    def clean_email(self):
        """
        Ensure the email address is not already registered.
        """
        email = self.cleaned_data.get("email")
        try:
            User.objects.exclude(id=self.instance.id).get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("This email is already registered"))

    def save(self, *args, **kwargs):
        """
        Create the new user using their email address as their username.
        """
        user = super(ProfileForm, self).save(*args, **kwargs)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
            user.save()

        # Save profile model.
        if self._has_profile:
            profile = user.get_profile()
            profile_fields_form = self.get_profile_fields_form()
            profile_fields_form(self.data, instance=profile).save()

        if self._signup:
            settings.use_editable()
            if settings.ACCOUNTS_VERIFICATION_REQUIRED:
                user.is_active = False
                user.save()
            else:
                user = authenticate(username=user.username,
                                    password=password, is_active=True)
        return user

    def get_profile_fields_form(self):
        return ProfileFieldsForm


class PasswordResetForm(Html5Mixin, forms.Form):
    """
    Validates the user's username or email for sending a login
    token for authenticating to change their password.
    """

    username = forms.CharField(label=_("Username or email address"))

    def clean(self):
        username = self.cleaned_data.get("username")
        username_or_email = Q(username=username) | Q(email=username)
        try:
            user = User.objects.get(username_or_email, is_active=True)
        except User.DoesNotExist:
            raise forms.ValidationError(
                             _("Invalid username/email"))
        else:
            self._user = user
        return self.cleaned_data

    def save(self):
        """
        Just return the authenticated user - used for sending login
        email.
        """
        return getattr(self, "_user", None)
