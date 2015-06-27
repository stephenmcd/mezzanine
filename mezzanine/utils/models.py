from __future__ import unicode_literals
from functools import partial
from future.utils import with_metaclass

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, Field
from django.db.models.signals import class_prepared
from django.utils import six

from mezzanine.utils.importing import import_dotted_path


def get_user_model_name():
    """
    Returns the app_label.object_name string for the user model.
    """
    return getattr(settings, "AUTH_USER_MODEL", "auth.User")


def base_concrete_model(abstract, instance):
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
    for cls in reversed(instance.__class__.__mro__):
        if issubclass(cls, abstract) and not cls._meta.abstract:
            return cls
    return instance.__class__


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


class LazyModelOperations(object):
    """
    This class connects itself to Django's class_prepared signal.
    Pass a function and a model or model name to its ``add()`` method,
    and the function will be called with the model as its only
    parameter once the model has been loaded. If the model is already
    loaded, the function is called immediately.

    Adapted from ``django.db.models.fields.related`` and used in
    ``mezzanine.generic.fields``.
    """

    def __init__(self):
        self.pending_operations = {}
        class_prepared.connect(self.signal_receiver)

    @staticmethod
    def model_key(model_or_name):
        """
        Returns an (app_label, model_name) tuple from a model or string.
        """
        if isinstance(model_or_name, six.string_types):
            app_label, model_name = model_or_name.split(".")
        else:
            # It's actually a model class.
            app_label = model_or_name._meta.app_label
            model_name = model_or_name._meta.object_name
        return app_label, model_name

    def add(self, function, *models_or_names):
        """
        The function passed to this method should accept n arguments,
        where n=len(models_or_names). When all the models are ready,
        the function will be called with the models as arguments, in
        the order they appear in this argument list.
        """

        # Eagerly parse all model strings so we can fail immediately
        # if any are plainly invalid.
        model_keys = [self.model_key(m) if not isinstance(m, tuple) else m
                      for m in models_or_names]

        # If this function depends on more than one model, recursively call add
        # for each, partially applying the given function on each iteration.
        model_key, more_models = model_keys[0], model_keys[1:]
        if more_models:
            inner_function = function
            function = lambda model: self.add(partial(inner_function, model),
                                              *more_models)

        # If the model is already loaded, pass it to the function immediately.
        # Otherwise, delay execution until the class is prepared.
        try:
            model_class = apps.get_registered_model(*model_key)
        except LookupError:
            self.pending_operations.setdefault(model_key, []).append(function)
        else:
            function(model_class)

    def signal_receiver(self, sender, **kwargs):
        """
        Receive ``class_prepared``, and pass the freshly prepared
        model to each function waiting for it.
        """
        key = (sender._meta.app_label, sender.__name__)
        for function in self.pending_operations.pop(key, []):
            function(sender)


lazy_model_ops = LazyModelOperations()
