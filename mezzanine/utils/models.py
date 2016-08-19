from __future__ import unicode_literals

import warnings

from future.utils import with_metaclass

from django.conf import settings
from django.contrib.auth import get_user_model as django_get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, Field

from mezzanine.utils.importing import import_dotted_path


def get_user_model():
    warnings.warn(
        "Mezzanine's get_user_model() is deprecated and will be removed in a "
        "future version. Replace all uses of this function with Django's "
        "django.contrib.auth.get_user_model().",
        DeprecationWarning
    )
    return django_get_user_model()


def get_user_model_name():
    """
    Returns the app_label.object_name string for the user model.
    """
    return getattr(settings, "AUTH_USER_MODEL", "auth.User")


def _base_concrete_model(abstract, klass):
    for kls in reversed(klass.__mro__):
        if issubclass(kls, abstract) and not kls._meta.abstract:
            return kls


def base_concrete_model(abstract, model):
    """
    Used in methods of abstract models to find the super-most concrete
    (non abstract) model in the inheritance chain that inherits from the
    given abstract model. This is so the methods in the abstract model can
    query data consistently across the correct concrete model.

    Consider the following::

        class Abstract(models.Model)

            class Meta:
                abstract = True

            def concrete(self):
                return base_concrete_model(Abstract, self)

        class Super(Abstract):
            pass

        class Sub(Super):
            pass

        sub = Sub.objects.create()
        sub.concrete() # returns Super

    In actual Mezzanine usage, this allows methods in the ``Displayable`` and
    ``Orderable`` abstract models to access the ``Page`` instance when
    instances of custom content types, (eg: models that inherit from ``Page``)
    need to query the ``Page`` model to determine correct values for ``slug``
    and ``_order`` which are only relevant in the context of the ``Page``
    model and not the model of the custom content type.
    """
    if hasattr(model, 'objects'):
        # "model" is a model class
        return (model if model._meta.abstract else
                _base_concrete_model(abstract, model))
    # "model" is a model instance
    return (
        _base_concrete_model(abstract, model.__class__) or
        model.__class__)


def upload_to(field_path, default):
    """
    Used as the ``upload_to`` arg for file fields - allows for custom
    handlers to be implemented on a per field basis defined by the
    ``UPLOAD_TO_HANDLERS`` setting.
    """
    from mezzanine.conf import settings
    for k, v in settings.UPLOAD_TO_HANDLERS.items():
        if k.lower() == field_path.lower():
            return import_dotted_path(v)
    return default


class AdminThumbMixin(object):
    """
    Provides a thumbnail method on models for admin classes to
    reference in the ``list_display`` definition.
    """

    admin_thumb_field = None

    def admin_thumb(self):
        thumb = ""
        if self.admin_thumb_field:
            thumb = getattr(self, self.admin_thumb_field, "")
        if not thumb:
            return ""
        from mezzanine.conf import settings
        from mezzanine.core.templatetags.mezzanine_tags import thumbnail
        x, y = settings.ADMIN_THUMB_SIZE.split('x')
        thumb_url = thumbnail(thumb, x, y)
        return "<img src='%s%s'>" % (settings.MEDIA_URL, thumb_url)
    admin_thumb.allow_tags = True
    admin_thumb.short_description = ""


class ModelMixinBase(type):
    """
    Metaclass for ``ModelMixin`` which is used for injecting model
    fields and methods into models defined outside of a project.
    This currently isn't used anywhere.
    """

    def __new__(cls, name, bases, attrs):
        """
        Checks for an inner ``Meta`` class with a ``mixin_for``
        attribute containing the model that this model will be mixed
        into. Once found, copy over any model fields and methods onto
        the model being mixed into, and return it as the actual class
        definition for the mixin.
        """
        if name == "ModelMixin":
            # Actual ModelMixin class definition.
            return super(ModelMixinBase, cls).__new__(cls, name, bases, attrs)
        try:
            mixin_for = attrs.pop("Meta").mixin_for
            if not issubclass(mixin_for, Model):
                raise TypeError
        except (TypeError, KeyError, AttributeError):
            raise ImproperlyConfigured("The ModelMixin class '%s' requires "
                                       "an inner Meta class with the "
                                       "``mixin_for`` attribute defined, "
                                       "with a value that is a valid model.")
        # Copy fields and methods onto the model being mixed into, and
        # return it as the definition for the mixin class itself.
        for k, v in attrs.items():
            if isinstance(v, Field):
                v.contribute_to_class(mixin_for, k)
            elif k != "__module__":
                setattr(mixin_for, k, v)
        return mixin_for


class ModelMixin(with_metaclass(ModelMixinBase, object)):
    """
    Used as a subclass for mixin models that inject their behaviour onto
    models defined outside of a project. The subclass should define an
    inner ``Meta`` class with a ``mixin_for`` attribute containing the
    model that will be mixed into.
    """
