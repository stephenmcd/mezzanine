=============
Configuration
=============

Mezzanine provides a central system for defining settings within
your project and applications that can then be edited by admin users.
The package ``mezzanine.conf`` contains the models for storing
editable settings in the database as well as the functions for
registering and loading these settings throughout your project.

.. _registering-settings:

Registering Settings
====================

Settings are defined by creating a module named ``defaults.py`` inside
one or more of the applications defined in your project's
``settings.INSTALLED_APPS`` setting. Inside your ``defaults.py`` module
you then call the function ``mezzanine.conf.register_setting`` for
each setting you want to define which takes several keyword arguments:

  * ``name``: The name of the setting.
  * ``label``: The verbose name of the setting for the admin.
  * ``description``: The description of the setting.
  * ``editable``: If ``True``, the setting will be editable via the admin.
  * ``default``: The default value of the setting.
  * ``choices``: A list of choices the user can select from when the
    setting is editable.
  * ``append``: If registering an existing setting, the default value
    given will be appended to the current.
  * ``translatable``: If ``django-modeltranslation`` is activated, this
    setting will store and display values on a per-language basis.

.. note::

    For settings registered with ``editable`` as ``True``, currently only
    strings, integers/floats and boolean values are supported for the
    ``default`` value.

For example suppose we had a ``authors`` application and we wanted to
create a setting that controls the number of books displayed per author
page, we would define the following in ``authors.defaults``::

    from mezzanine.conf import register_setting

    register_setting(
        name="AUTHORS_BOOKS_PER_PAGE",
        label="Authors books per page",
        description="The number of books to show per author page.",
        editable=True,
        default=10,
    )

.. note::

    If you are using Django 1.7 or greater and your app is included in your
    INSTALLED_APPS as an AppConfig (eg authors.apps.MyCrazyConfig), Mezzanine
    won't import your defaults.py automatically. Instead you must import it
    manually in your AppConfig's ready() method.

Reading Settings
================

Mezzanine provides a settings object via ``mezzanine.conf.settings`` in a
similar way to Django's ``django.conf.settings``. This settings object
contains each of the settings registered above using their names as
attributes. Continuing on from our previous example, suppose we have a view
for photos::

    from django.shortcuts import render
    from mezzanine.conf import settings
    from .models import Book

    def books_view(request):
        books = Book.objects.all()[:settings.AUTHORS_BOOKS_PER_PAGE]
        return render(request, "books.html", {"books": books})

When defining editable settings, care should be taken when considering
where in your project the setting will be used. For example if a setting
is used in a ``urlpattern`` or the creation of a ``model`` class it would
only be read when your site is first loaded, and therefore having it
change at a later point by an admin user would not have any effect without
reloading your entire project. In the snippet above, since the settings is
being read within a view, the value of the setting being accessed is
loaded each time the view is run. This ensures that if the value of the
setting has been changed by an admin user it will be reflected on
the website.

.. note::

    It's also important to realize that with any settings flagged as
    editable, defining a value for these in your project's
    ``settings.py`` will only serve to provide their default values.
    Once editable settings are modified via the admin, their values
    stored in the database will always be used.

Django Settings
===============

Mezzanine's settings object integrates with Django's settings object in a
couple of ways.

Firstly it's possible to override the default value for any setting defined
using ``mezzanine.conf.register_setting`` by adding its name and value as
a regular setting to your project's settings module. This is especially useful
when any of your project's ``INSTALLED_APPS`` (including Mezzanine
itself) register settings that aren't editable and you want to override
these settings without modifying the application that registered them.

Secondly it's possible to access any of the settings defined by Django or
your project's settings module via Mezzanine's settings object in the same
way you would use Django's settings object. This allows for a single access
point for all settings regardless of how they are defined.

Default Settings
================

Mezzanine defines the following settings:

.. include:: settings.rst
