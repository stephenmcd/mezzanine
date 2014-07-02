from __future__ import unicode_literals

from django.utils.datastructures import SortedDict

from mezzanine import template
from mezzanine.conf import settings
from mezzanine.utils.models import get_user_model
from mezzanine.accounts import (get_profile_form, get_profile_user_fieldname,
                                get_profile_for_user, ProfileNotConfigured)
from mezzanine.accounts.forms import LoginForm


register = template.Library()

User = get_user_model()


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


@register.filter
def profile_fields(user):
    """
    Returns profile fields as a dict for the given user. Used in the
    profile view template when the ``ACCOUNTS_PROFILE_VIEWS_ENABLED``
    setting is set to ``True``, and also in the account approval emails
    sent to administrators when the ``ACCOUNTS_APPROVAL_REQUIRED``
    setting is set to ``True``.
    """
    fields = SortedDict()
    try:
        profile = get_profile_for_user(user)
        user_fieldname = get_profile_user_fieldname()
        exclude = tuple(settings.ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS)
        for field in profile._meta.fields:
            if field.name not in ("id", user_fieldname) + exclude:
                value = getattr(profile, field.name)
                fields[field.verbose_name.title()] = value
    except ProfileNotConfigured:
        pass
    return list(fields.items())


@register.filter
def username_or(user, attr):
    """
    Returns the user's username for display, or an alternate attribute
    if ``ACCOUNTS_NO_USERNAME`` is set to ``True``.
    """
    if not settings.ACCOUNTS_NO_USERNAME:
        attr = "username"
    value = getattr(user, attr)
    if callable(value):
        value = value()
    return value
