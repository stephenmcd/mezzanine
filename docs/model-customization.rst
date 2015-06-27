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
(or any library's) models.

.. note::

    Using the following approach comes with certain trade-offs
    described below in :ref:`field-injection-caveats`. Be sure to fully
    understand these prior to using the ``EXTRA_MODEL_FIELDS`` setting.

Each item in the ``EXTRA_MODEL_FIELDS`` sequence is a four item
sequence. The first two items are the dotted path to the model and its
field name to be added, and the dotted path to the field class to use
for the field. The third and fourth items are a sequence of positional
args and a dictionary of keyword args, to use when creating the field
instance.

For example suppose you want to inject a custom ``ImageField`` from a
third party library into Mezzanine's ``BlogPost`` model, you would
define the following in your project’s settings module::

    EXTRA_MODEL_FIELDS = (
        # Four-item sequence for one field injected.
        (
            # Dotted path to field.
            "mezzanine.blog.models.BlogPost.image",
            # Dotted path to field class.
            "somelib.fields.ImageField",
            # Positional args for field class.
            ("Image",),
            # Keyword args for field class.
            {"blank": True, "upload_to: "blog"},
        ),
    )

Each ``BlogPost`` instance will now have an ``image`` attribute, using the
``ImageField`` class defined in the fictitious ``somelib.fields`` module.

Another interesting example would be adding a field to all of Mezzanine's
content types by injecting fields into the ``Page`` class. Continuing on
from the previous example, suppose you wanted to add a regular Django
``IntegerField`` to all content types::

    EXTRA_MODEL_FIELDS = (
        (
            "mezzanine.blog.models.BlogPost.image",
            "somelib.fields.ImageField",
            ("Image",),
            {"blank": True, "upload_to": "blog"},
        ),
        # Example of adding a field to *all* of Mezzanine's content types:
        (
            "mezzanine.pages.models.Page.another_field",
            "IntegerField", # 'django.db.models.' is implied if path is omitted.
            ("Another name",),
            {"blank": True, "default": 1},
        ),
    )

Note here that the full path for the field class isn't required since a
regular Django field is used - the ``django.db.models.`` path is implied.

.. _field-injection-caveats:

Field Injection Caveats
=======================

The above technique provides a great way of avoiding the performance
penalties of SQL JOINS required by the traditional approach of
`subclassing models <https://docs.djangoproject.com/en/1.3/topics/db/models/#multi-table-inheritance>`_,
however some extra consideration is required when used with the
migrations management commands included in Django starting from
version 1.7. In the first example above, Django's ``makemigrations``
command views the new ``image`` field on the
``BlogPost`` model of the ``mezzanine.blog`` app. As such, in order to
create a migration for it, the migration must be created for the blog
app itself and by default would end up in the migrations directory of
the blog app, which completely goes against the notion of not
modifying the blog app to add your own custom fields.

One approach to address this is to use Django's
`MIGRATION_MODULES <https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-MIGRATION_MODULES>`_
setting and locate your own migration files somewhere in your project
or app. However, if you define a custom directory to store migrations
for an app with injected field (e.g: ``pages`` in the second example
above), make sure to do the same for apps that define models that are
subclasses of the one you are injecting fields into. Failing to do so
will result in broken dependencies for migration files.

The configuration for the second example should containt at least
something that looks like::

    MIGRATION_MODULES = {
        "pages": "path.to.migration.storage.pages_migration",
        "forms": "path.to.migration.storage.forms_migration",
        "galleries": "path.to.migration.storage.galleries_migration",
    }

To create the new migration files and apply the changes, simply run::

    $ python manage.py makemigrations
    $ python manage.py migrate

Be warned that over time this approach will almost certainly require
some manual intervention by way of editing migrations, or modifying
the database manually to create the correct state. Ultimately there is
a trade-off involved here.

Admin Fields
============

Whether using the above approach to inject fields into models, or
taking the more traditional approach of subclassing models, most
often you will also want to expose new fields to the admin interface.
This can be achieved by simply unregistering the relevant admin class,
subclassing it, and re-registering your new admin class for the
associated model. Continuing on from the first example, the code below
takes a copy of the ``fieldsets`` definition for the original
``BlogPostAdmin``, and injects our custom field's name into the
desired position.::

    # In myapp/admin.py

    from copy import deepcopy
    from django.contrib import admin
    from mezzanine.blog.admin import BlogPostAdmin
    from mezzanine.blog.models import BlogPost

    blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
    blog_fieldsets[0][1]["fields"].insert(-2, "image")

    class MyBlogPostAdmin(BlogPostAdmin):
        fieldsets = blog_fieldsets

    admin.site.unregister(BlogPost)
    admin.site.register(BlogPost, MyBlogPostAdmin)
