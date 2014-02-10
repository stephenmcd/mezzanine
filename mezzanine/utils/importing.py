from __future__ import unicode_literals

import os

import django
from django.utils.importlib import import_module


def path_for_import(name):
    """
    Returns the directory path for the given package or module.
    """
    return os.path.dirname(os.path.abspath(import_module(name).__file__))


def import_dotted_path(path):
    """
    Takes a dotted path to a member name in a module, and returns
    the member after importing it.
    """
    try:
        module_path, member_name = path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, member_name)
    except (ValueError, ImportError, AttributeError) as e:
        raise ImportError("Could not import the name: %s: %s" % (path, e))


def get_app_name_list():
    if django.VERSION >= (1, 7):
        from django.apps import apps as django_apps
        for app in django_apps.get_app_configs():
            yield app.name
    else:
        from django.conf import settings
        for app in settings.INSTALLED_APPS:
            yield app
