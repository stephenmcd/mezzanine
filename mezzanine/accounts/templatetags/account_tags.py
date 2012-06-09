
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from mezzanine.accounts.forms import LoginForm, ProfileForm, PasswordResetForm
from mezzanine import template


register = template.Library()

@register.inclusion_tag("accounts/account_tag_login.html", takes_context=True)
def login_form(context, next):
    """
    Login form template tag
    """
    context["form"] = LoginForm()
    context["title"] = _("Login")
    context["next"] = next
    return context

@register.inclusion_tag("accounts/account_tag_profile.html", takes_context=True)
def profile_form(context):
    """
    Profile form for sign up or profile update template tag
    """
    context["form"] = ProfileForm()
    context["title"] = _("Signup")
    return context