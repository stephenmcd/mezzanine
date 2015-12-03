===================
Multi-Lingual Sites
===================

Mezzanine provides optional support for `django-modeltranslation
<https://readthedocs.org/projects/django-modeltranslation/>`_ which
enables content editors to provide multi-lingual content to support
sites in multiple languages.

.. note::
    Mezzanine only provides the integration of django-modeltranslation.
    For dedicated assistance, please check out the documentation for
    django-modeltranslation: `documentation
    <https://readthedocs.org/projects/django-modeltranslation/>`_ or
    its `code <https://github.com/deschler/django-modeltranslation>`_.

Translation Fields in Mezzanine
===============================

In order to enable translation fields for Mezzanine content, you will
need to install django-modeltranslation and activate the app in your
``settings.py``. Once you have `installed django-modeltranslation
<http://django-modeltranslation.readthedocs.org/en/latest/installation.html>`_,
you can enable support for it by setting the ``USE_MODELTRANSLATION``
setting to ``True`` in your project's ``settings.py`` module, and
also defining at least two entries in the ``LANGUAGES`` setting.

For new projects, ``manage.py createdb`` will take care of creating
extra columns in the database for each language. For current or
older projects, you can catch up by running
``manage.py sync_translation_fields`` and then
``manage.py update_translation_fields``.

.. note::
    A django-modeltranslation setting that can help managing the
    transition for content *partially* in several languages is
    ``MODELTRANSLATION_FALLBACK_LANGUAGES``.  This setting allows you
    to avoid having empty content when the translation is not provided
    for a specific language. Please consult `django-modeltranslation's
    documentation
    <http://django-modeltranslation.readthedocs.org/en/latest/usage.html#fallback-languages>`_
    for more detail.

Translation Fields for Custom Applications
==========================================

For models that don't inherit from Mezzanine's models, again please consult
`django-modeltranslation's documentation
<http://django-modeltranslation.readthedocs.org/en/latest/registration.html>`_.
To start with, you'll need to provide a ``translation.py`` module,
containing classes describing which of your model fields you wish to
translate, as well as registering your models using the
``modeltranslation.translator.translator.register`` method.

For models that extends Mezzanine capabilities, there are two rules:

Firstly, the app in which your model is defined must be listed *after*
the app it is extending from in your ``INSTALLED_APPS``
setting. For example, ``mezzanine.forms`` extends models from
``mezzanine.pages`` and should appear after it.

.. note::
    If your app defines both models that need to be translated and
    static content or templates that override default ones from
    Mezzanine, you'll need to split your app to distinguish
    between presentation and content. This is due to conflicting
    ideas with translated model inheritance, and template or static
    file overriding, in regard to the order of ``INSTALLED_APPS``.

Secondly, for an external app, create a ``translation.py`` module
at the root of your app. The content of this file might benefit
from ``mezzanine.core.translation`` depending on what you are
extending from. For example, to improve the model from
:doc:`content-architecture` and provide translatable fields::

    from django.db import models
    from mezzanine.pages.models import Page

    class Author(Page):
        dob = models.DateField("Date of birth")
        trivia = models.TextField("Trivia")

    class Book(models.Model):
        author = models.ForeignKey("Author")
        cover = models.ImageFiled(upload_to="authors")
        title = models.CharField("Title", max_length=200)

A corresponding ``translation.py`` module in this app would look like::

    from modeltranslation.translator import translator, TranslationOptions
    from .models import Author, Book

    class TranslatedAuthor(TranslationOptions):
        fields = ('trivia',)

    class TranslatedBook(TranslationOptions):
        fields = ('title',)

    translator.register(Author, TranslatedAuthor)
    translator.register(Book, TranslatedBook)

In this case, please note ``mezzanine.pages.translation.TranslatedPage``
is not referenced in any way. This is due to the fact that
``mezzanine.pages.models.Page`` is not abstract, and thus has its own
table in the database. The fields have already been registered for
translation and django-modeltranslation will happily handle it for you.

If you want to extend an abstract model, such as
``mezzanine.core.models.Slugged`` or ``mezzanine.core.models.Displayable``,
you will need to subclass their translation registration. An example of
this is the ``mezzanine.blog`` app in its ``translation.py`` module::

    from modeltranslation.translator import translator
    from mezzanine.core.translation import (TranslatedSlugged,
                                            TranslatedDisplayable,
                                            TranslatedRichText)
    from mezzanine.blog.models import BlogCategory, BlogPost

    class TranslatedBlogPost(TranslatedDisplayable, TranslatedRichText):
        fields = ()

    class TranslatedBlogCategory(TranslatedSlugged):
        fields = ()

    translator.register(BlogPost, TranslatedBlogPost)
    translator.register(BlogCategory, TranslatedBlogCategory)

You don't add translatable fields in your model beside those
already defined inside Mezzanine's models. You need to extend from
``mezzanine.core.translation`` classes, so django-modeltranslation is aware of
the abstract fields it will have to manage.

After that, you can ``manage.py createdb`` for a new project or
``manage.py sync_translation_fields`` and then
``manage.py update_translation_fields`` for an existing one.

Translation Fields and Migrations
=================================

Mezzanine is shipped with its own migration files but these do not take
translation fields into account. These fields are created by every
project's ``LANGUAGES`` setting and thus can't be provided by default.
If you want to both manage migrations for your project and enable
translation fields, there are two possibilities.

Either you disable translation fields while managing your migrations
as usual and then catch up by adding the missing fields if any::

    # edit settings.py to set USE_MODELTRANSLATION = False
    $ python manage.py makemigrations
    $ python manage.py migrate
    # edit settings.py to set USE_MODELTRANSLATION back to True
    $ python manage.py sync_translation_fields

This way, your migration files will never contains references to your
specific ``LANGUAGES`` setting.

Or you create migration files including all the translation fields
for your project. This way you won't need to rely on the
``manage.py sync_translation_fields`` command anymore. You will
need to define a custom ``MIGRATION_MODULES`` and then run::

     $ python manage.py makemigrations

Have a look at :ref:`field-injection-caveats` for a better introduction
to ``MIGRATION_MODULES``.

Translation for Injected Fields
===============================

If you added fields in Mezzanine's models through ``EXTRA_MODEL_FIELDS``
and want to add translations, you will need to create a custom app that
will hold the necessary ``translation.py`` module.

Adding a translation field to all of Mezzanine's content type would
look like::

  EXTRA_MODEL_FIELDS = (
      (
          "mezzanine.pages.models.Page.quote",
          "TextField",
          ("Page's Quote",),
          {"blank": True},
      ),
  )

The app containing the corresponding ``translation.py`` module should
be defined *after* ``mezzanine.pages`` in ``INSTALLED_APPS`` but
*before* any app that contains models that subclass
``mezzanine.pages.models.Page`` (such as ``mezzanine.forms``,
``mezzanine.galleries`` or ``cartridge.shop``). The ``translation.py``
file itself would be::

    from modeltranslation.translator import translator
    from mezzanine.pages.translation import TranslatedPage
    from mezzanine.pages.models import Page

    class TranslatedInjectedPage(TranslatedPage):
        field = ('quote',),

    translator.unregister(Page)
    translator.register(Page, TranslatedInjectedPage)

Redistributable Applications for Mezzanine
==========================================

If you want to provide translation support for your Mezzanine app,
make sure it works with both ``USE_MODELTRANSLATION`` set to ``True``
or ``False``. Mezzanine enforces the value to ``False`` if
django-modeltranslation is not installed.

The ``USE_MODELTRANSLATION`` setting can therefore be used to check
against, when extra steps are required (such as saving an instance of
a model in every language). In the case of a project with
``USE_MODELTRANSLATION`` set to ``False``, the ``translation.py``
module will just be ignored.

The ``USE_MODELTRANSLATION`` setting is also available in the
template's ``settings`` variable. Have a look at the
``includes/language_selector.html`` template in ``mezzanine.core``
for a working example.
