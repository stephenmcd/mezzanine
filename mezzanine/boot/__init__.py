"""
An app that is forced to the top of the list in ``INSTALLED_APPS``
for the purpose of hooking into Django's ``class_prepared`` signal
and adding custom fields as defined by the ``EXTRA_MODEL_FIELDS``
setting.
"""

from collections import defaultdict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import class_prepared

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
