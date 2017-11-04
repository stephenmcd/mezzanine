import django
from django.conf import settings


# Middleware mixin for Django 1.10
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


def get_middleware_setting_name():
    return "MIDDLEWARE" if hasattr(settings, 'MIDDLEWARE') \
                                        and settings.MIDDLEWARE is not None \
                                        else "MIDDLEWARE_CLASSES"


def get_middleware_setting():
    return getattr(settings, get_middleware_setting_name())


def is_authenticated(user):
    if django.VERSION < (1, 10):
        return user.is_authenticated()
    return user.is_authenticated
