
from django.contrib.auth import (authenticate, login as auth_login,
                                               logout as auth_logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import info, error
from django.core.urlresolvers import NoReverseMatch
from django.shortcuts import get_object_or_404, redirect
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from mezzanine.accounts import get_profile_model, get_profile_user_fieldname
from mezzanine.accounts import get_profile_form
from mezzanine.accounts.forms import LoginForm, PasswordResetForm
from mezzanine.conf import settings
from mezzanine.utils.email import send_verification_mail
from mezzanine.utils.urls import login_redirect
from mezzanine.utils.views import render


def login(request, template="accounts/account_login.html"):
    """
    Login form.
    """
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        authenticated_user = form.save()
        info(request, _("Successfully logged in"))
        auth_login(request, authenticated_user)
        return login_redirect(request)
    context = {"form": form, "title": _("Login")}
    return render(request, template, context)


def logout(request):
    """
    Log the user out.
    """
    auth_logout(request)
    info(request, _("Successfully logged out"))
    return redirect(request.GET.get("next", "/"))


def signup(request, template="accounts/account_signup.html"):
    """
    Signup form.
    """
    profile_form = get_profile_form()
    form = profile_form(request.POST or None)
    if request.method == "POST" and form.is_valid():
        new_user = form.save()
        if not new_user.is_active:
            send_verification_mail(request, new_user, "signup_verify")
            info(request, _("A verification email has been sent with "
                            "a link for activating your account."))
            return redirect(request.GET.get("next", "/"))
        else:
            info(request, _("Successfully signed up"))
            auth_login(request, new_user)
            return login_redirect(request)
    context = {"form": form, "title": _("Signup")}
    return render(request, template, context)


def signup_verify(request, uidb36=None, token=None):
    """
    View for the link in the verification email sent to a new user
    when they create an account and ``ACCOUNTS_VERIFICATION_REQUIRED``
    is set to ``True``. Activates the user and logs them in,
    redirecting to the URL they tried to access when signing up.
    """
    user = authenticate(uidb36=uidb36, token=token, is_active=False)
    if user is not None:
        user.is_active = True
        user.save()
        auth_login(request, user)
        info(request, _("Successfully signed up"))
        return login_redirect(request)
    else:
        error(request, _("The link you clicked is no longer valid."))
        return redirect("/")


@login_required
def profile_redirect(request):
    """
    Just gives the URL prefix for profiles an action - redirect
    to the logged in user's profile.
    """
    return redirect("profile", username=request.user.username)


def profile(request, username, template="accounts/account_profile.html"):
    """
    Display a profile.
    """
    profile_user = get_object_or_404(
        User,
        username__iexact=username,
        is_active=True
    )
    profile_fields = SortedDict()
    Profile = get_profile_model()
    if Profile is not None:
        profile = profile_user.get_profile()
        user_fieldname = get_profile_user_fieldname()
        exclude = tuple(settings.ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS)
        for field in Profile._meta.fields:
            if field.name not in ("id", user_fieldname) + exclude:
                value = getattr(profile, field.name)
                profile_fields[field.verbose_name.title()] = value
    context = {
        "profile_user": profile_user,
        "profile_fields": profile_fields.items(),
    }
    return render(request, template, context)


@login_required
def account_redirect(request):
    """
    Just gives the URL prefix for accounts an action - redirect
    to the profile update form.
    """
    return redirect("profile_update")


@login_required
def profile_update(request, template="accounts/account_profile_update.html"):
    """
    Profile update form.
    """
    profile_form = get_profile_form()
    form = profile_form(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        info(request, _("Profile updated"))
        try:
            return redirect("profile", username=user.username)
        except NoReverseMatch:
            return redirect("profile_update")
    context = {"form": form, "title": _("Update Profile")}
    return render(request, template, context)


def password_reset(request, template="accounts/account_password_reset.html"):
    form = PasswordResetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        send_verification_mail(request, user, "password_reset_verify")
        info(request, _("A verification email has been sent with "
                        "a link for resetting your password."))
    context = {"form": form, "title": _("Password Reset")}
    return render(request, template, context)


def password_reset_verify(request, uidb36=None, token=None):
    user = authenticate(uidb36=uidb36, token=token, is_active=True)
    if user is not None:
        auth_login(request, user)
        return redirect("profile_update")
    else:
        error(request, _("The link you clicked is no longer valid."))
        return redirect("/")
