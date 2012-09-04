"""
An app that is forced to the top of the list in ``INSTALLED_APPS``
for the purpose of hooking into Django's ``class_prepared`` signal
and adding custom fields as defined by the ``EXTRA_MODEL_FIELDS``
setting. Also patches ``django.contrib.admin.site`` to use
``LazyAdminSite`` that defers certains register/unregister calls
until ``admin.autodiscover`` to avoid some timing issues around
custom fields not being available when custom admin classes are
registered.
"""

from collections import defaultdict

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import class_prepared

from mezzanine.boot.lazy_admin import LazyAdminSite
from mezzanine.utils.importing import import_dotted_path


# Convert ``EXTRA_MODEL_FIELDS`` into a more usable structure, a
# dictionary mapping module.model paths to dicts of field names mapped
# to field instances to inject, with some sanity checking to ensure
# the field is importable and the arguments given for it are valid.
fields = defaultdict(dict)
for entry in getattr(settings, "EXTRA_MODEL_FIELDS", []):
    model_path, field_name = entry[0].rsplit(".", 1)
    field_path, field_args, field_kwargs = entry[1:]
    if "." not in field_path:
        field_path = "django.db.models.%s" % field_path
    try:
        field_class = import_dotted_path(field_path)
    except ImportError:
        raise ImproperlyConfigured("The EXTRA_MODEL_FIELDS setting contains "
                                   "the field '%s' which could not be "
                                   "imported." % entry[1])
    try:
        field = field_class(*field_args, **field_kwargs)
    except TypeError, e:
        raise ImproperlyConfigured("The EXTRA_MODEL_FIELDS setting contains "
                                   "arguments for the field '%s' which could "
                                   "not be applied: %s" % (entry[1], e))
    fields[model_path][field_name] = field


def add_extra_model_fields(sender, **kwargs):
    """
    Injects custom fields onto the given sender model as defined
    by the ``EXTRA_MODEL_FIELDS`` setting.
    """
    model_path = "%s.%s" % (sender.__module__, sender.__name__)
    for field_name, field in fields.get(model_path, {}).items():
        field.contribute_to_class(sender, field_name)


if fields:
    class_prepared.connect(add_extra_model_fields, dispatch_uid="FQFEQ#rfq3r")


# Override django.contrib.admin.site with LazyAdminSite. It must
# be bound to a separate name (admin_site) for access in autodiscover
# below.

admin_site = LazyAdminSite()
admin.site = admin_site
django_autodiscover = admin.autodiscover


def autodiscover(*args, **kwargs):
    """
    Replaces django's original autodiscover to add a call to
    LazyAdminSite's lazy_registration.
    """
    django_autodiscover(*args, **kwargs)
    admin_site.lazy_registration()

admin.autodiscover = autodiscover
