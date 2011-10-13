===================
Model Customization
===================

So far under :doc:`content-architecture` the concept of subclassing
Mezzanine's models has been described. This section describes the hooks
Mezzanine provides for directly modifying the behaviour of its models.

Field Injection
===============

Mezzanine provides the setting ``EXTRA_MODEL_FIELDS`` which allows you
to define a sequence of fields that will be injected into Mezzanine's
(or any library's) models. Each item in the sequence is a three
item sequence, containing the dotted path to the model and its field
name to be added, the dotted path to the field class to use for the
field, and a dictionary of keyword args to use when creating the field.

For example suppose you want to inject a custom ``ImageField`` from a
third party library into Mezzanine's ``BlogPost`` model, you would
define the following in your projects’s settings module::

    from django.utils.translation import ugettext as _
    EXTRA_MODEL_FIELDS = (
        ("mezzanine.blog.models.BlogPost.image", "somelib.fields.ImageField", {
            "verbose_name": _("Image"), "blank": True, "upload_to: "blog"
        }),
    )

Each ``BlogPost`` instance will now have an ``image`` attribute, using the
``ImageField`` class defined in the fictitious ``somelib.fields`` module.

Another interesting example would be adding a field to all of Mezzanine's
content types by injecting fields into the ``Page`` class. Continuing on
from the previous example, suppose you wanted to add a regular Django
``IntegerField`` to all content types::

    from django.utils.translation import ugettext as _
    EXTRA_MODEL_FIELDS = (
        ("mezzanine.blog.models.BlogPost.image", "somelib.fields.ImageField", {
            "verbose_name": _("Image"), "blank": True, "upload_to: "blog"
        }),
        # Example of adding a field to *all* of Mezzanine's content types:
        ("mezzanine.pages.models.Page.another_field", "IntegerField", {
            "verbose_name": _("Another name"), "blank": True, "default": 1
        }),
    )

Note here that the full path for the field class isn't required since a
regular Django field is used - the ``django.db.models.`` path is implied.

.. TODO:
   Admin unregister/subclass/register example
   Notes about how boot works with class_prepared
   Notes about migrations

