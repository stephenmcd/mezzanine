
from django.contrib.auth.models import User

from mezzanine import template
from mezzanine.accounts.forms import LoginForm
from mezzanine.accounts import get_profile_form

register = template.Library()


@register.as_tag
def login_form(*args):
    """
    Returns the login form:

    {% login_form as form %}
    {{ form }}

    """
    return LoginForm()


@register.as_tag
def signup_form(*args):
    """
    Returns the signup form:

    {% signup_form as form %}
    {{ form }}

    """
    return get_profile_form()()


@register.as_tag
def profile_form(user):
    """
    Returns the profile form for a user:

    {% if request.user.is_authenticated %}
    {% profile_form request.user as form %}
    {{ form }}
    {% endif %}

    """
    if isinstance(user, User):
        return get_profile_form()(instance=user)
    return ""
