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

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured

from mezzanine.boot.lazy_admin import LazyAdminSite
from mezzanine.utils.importing import import_dotted_path


def parse_field_path(field_path):
    """
    Take a path to a field like "mezzanine.pages.models.Page.feature_image"
    and return a model key, which is a tuple of the form ('pages', 'page'),
    and a field name, e.g. "feature_image".
    """
    model_path, field_name = field_path.rsplit(".", 1)
    app_name, model_name = model_path.split(".models.")
    _, app_label = app_name.rsplit(".", 1)
    return (app_label, model_name.lower()), field_name


def import_field(field_classpath):
    """
    Imports a field by its dotted class path, prepending "django.db.models"
    to raw class names and raising an exception if the import fails.
    """
    if "." in field_classpath:
        fully_qualified = field_classpath
    else:
        fully_qualified = "django.db.models.%s" % field_classpath
    try:
        return import_dotted_path(fully_qualified)
    except ImportError:
        raise ImproperlyConfigured(
            "The EXTRA_MODEL_FIELDS setting contains "
            "the field '%s' which could not be "
            "imported." % field_classpath
        )


def parse_extra_model_fields(extra_model_fields):
    """
    Parses the value of EXTRA_MODEL_FIELDS, grouping the entries by model
    and instantiating the extra fields. Returns a sequence of tuples of
    the form (model_key, fields) where model_key is a pair of app_label,
    model_name and fields is a list of (field_name, field_instance) pairs.
    """
    fields = defaultdict(list)
    for entry in extra_model_fields:
        model_key, field_name = parse_field_path(entry[0])
        field_class = import_field(entry[1])
        field_args, field_kwargs = entry[2:]
        try:
            field = field_class(*field_args, **field_kwargs)
        except TypeError as e:
            raise ImproperlyConfigured(
                "The EXTRA_MODEL_FIELDS setting contains arguments for the "
                "field '%s' which could not be applied: %s" % (entry[1], e)
            )
        fields[model_key].append((field_name, field))
    return fields


fields = parse_extra_model_fields(getattr(settings, "EXTRA_MODEL_FIELDS", []))


def add_extra_model_fields(sender, **kwargs):
    """
    Injects custom fields onto the given sender model as defined
    by the ``EXTRA_MODEL_FIELDS`` setting. This is a closure over
    the "fields" variable.
    """
    model_key = sender._meta.app_label, sender._meta.model_name
    for field_name, field in fields.get(model_key, {}):
        field.contribute_to_class(sender, field_name)


for model_key in fields:
    apps.lazy_model_operation(add_extra_model_fields, model_key)


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
