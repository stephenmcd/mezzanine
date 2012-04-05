
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import info, error
from django.shortcuts import redirect
from django.utils.http import base36_to_int
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.accounts.forms import LoginForm, SignupForm
from mezzanine.utils.email import send_verification_mail
from mezzanine.utils.views import render


def account(request, template="account.html"):
    """
    Display and handle both the login and signup forms.
    """
    login_form = LoginForm(request)
    signup_form = SignupForm(request)
    if request.method == "POST":
        posted_form = None
        message = ""
        if request.POST.get("login") is not None:
            login_form = LoginForm(request, request.POST)
            if login_form.is_valid():
                posted_form = login_form
                message = _("Successfully logged in")
        else:
            signup_form = SignupForm(request, request.POST)
            if signup_form.is_valid():
                new_user = signup_form.save()
                if not new_user.is_active:
                    send_verification_mail(request, new_user)
                    info(request, _("A verification email has been sent with "
                                    "a link for activating your account."))
                else:
                    posted_form = signup_form
                    message = _("Successfully signed up")
        if posted_form is not None:
            posted_form.login(request)
            info(request, message)
            return redirect(request.GET.get("next", "/"))
    context = {"login_form": login_form, "signup_form": signup_form}
    return render(request, template, context)


def verify_account(request, uidb36=None, token=None):
    """
    View for the link in the verification email sent to a new user
    when they create an account and ``ACCOUNTS_VERIFICATION_REQUIRED``
    is set to ``True``. Activates the user and logs them in,
    redirecting to the URL they tried to access when signing up.
    """
    user = None
    if uidb36 and token:
        try:
            user = User.objects.get(is_active=False, id=base36_to_int(uidb36))
        except User.DoesNotExist:
            pass
        else:
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                user.backend = settings.AUTHENTICATION_BACKENDS[0]
                login(request, user)
            else:
                user = None
    url = request.GET.get("next", "/")
    if user is None:
        error(request, _("The link you clicked is no longer valid."))
        url = "/"
    return redirect(url)


def logout(request):
    """
    Log the user out.
    """
    auth_logout(request)
    info(request, _("Successfully logged out"))
    return redirect(request.GET.get("next", "/"))
