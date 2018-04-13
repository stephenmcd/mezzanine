"""
Various utils for dealing with backward compatibility across Django
versions.
"""
from functools import wraps

import django
from django.conf import settings


# Middleware mixin for Django 1.10
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


def get_middleware_setting_name():
    """
    Returns the name of the middleware setting.
    """
    if hasattr(settings, "MIDDLEWARE") and settings.MIDDLEWARE is not None:
        return "MIDDLEWARE"
    else:
        return "MIDDLEWARE_CLASSES"


def get_middleware_setting():
    """
    Returns the middleware setting.
    """
    return getattr(settings, get_middleware_setting_name())


def is_authenticated(user):
    """
    Returns True if the user is authenticated.
    """
    if django.VERSION < (1, 10):
        return user.is_authenticated()
    return user.is_authenticated


def get_related_model(field):
    """
    Returns the model on a relation field.
    """
    # We could skip the version check here and rely on AttributeError,
    # but that triggers all the deprecation warnings for this.
    if django.VERSION < (1, 9):
        try:
            return field.rel.to
        except AttributeError:
            pass
    else:
        try:
            return field.remote_field.model
        except AttributeError:
            pass


def mark_safe(s):
    from django.utils.safestring import mark_safe as django_safe
    if callable(s):
        @wraps(s)
        def wrapper(*args, **kwargs):
            return django_safe(*args, **kwargs)
        return wrapper
    return django_safe(s)
