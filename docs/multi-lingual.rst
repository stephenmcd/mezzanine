===================
Multi-Lingual Sites
===================

Mezzazine comes coupled to `django-modeltranslation
<https://readthedocs.org/projects/django-modeltranslation/>`_ and provides
the optionnal ability to enable translation for your models content.

.. note::
    Mezzanine only provides the integration of django-modeltranslation. For
    dedicated assistance please check out their `documentation
    <https://readthedocs.org/projects/django-modeltranslation/>`_ or their
    `code <https://github.com/deschler/django-modeltranslation>`_.

Enabling Translation Fields in Mezzanine
========================================

In order to enable translation fields for mezzanine content, you will need to
both install django-modeltranslation and activate it in your ``settings.py``.

The former is generally done using ``pip install django-modeltranslation`` but
`other methods exists
<http://django-modeltranslation.readthedocs.org/en/latest/installation.html>`_.
The latter is simply done by having ``USE_MODELTRANSLATION = True`` in your
``settings.py`` and defining at least two ``LANGUAGES``.

For new projects, ``manage.py createdb`` will take care of creating extraneous
columns in the database for each language. For older ones, you can catch up
by running ``manage.py sync_translation_fields`` and then
``manage.py update_translation_fields``.

.. note::
    A modeltranslation setting that can help managing the transition when
    content is partially in several languages is
    ``MODELTRANSLATION_FALLBACK_LANGUAGES``. It can help avoiding blank
    content when translation is not provided for some languages. Check
    `their documentation
    <http://django-modeltranslation.readthedocs.org/en/latest/usage.html#fallback-languages>`_
    to understand how.

Enabling Translation Fields for Custom Applications
===================================================

For models that don't inherit from mezzanine models, it is a simple matter of
following `the documentation
<http://django-modeltranslation.readthedocs.org/en/latest/registration.html>`_. 
Mainly, you'll have to provide a ``translation.py`` file containing classes
describing which fields of your models you wish to translate and registering
your models using the ``modeltranslation.translator.translator.register``
method.

For models that extends mezzanine capabilities, two rules are to be followed.
First and foremost, the application in which your model is defined should be
listed *after* the application it is extending from in your ``INSTALLED_APPS``
setting. For example, ``mezzanine.forms`` extends models from
``mezzanine.pages`` and thus should appear after it.

.. note::
    If your application defines both models that need to be translated and
    static content or templates that overide default ones from mezzanine, it
    may means that you will want to place it both before ``mezzanine.pages``
    (to benefit from the static files finder) and after it in ``INSTALLED_APPS``
    (to enable translations). In this case consider splitting your application
    and distinguish between presentation and content.

The second thing to do is, as for an external application, to create a
``translation.py`` file at the root of your application. The content of this
file might benefit from ``mezzanine.core.translation`` 
depending what you are extending from.

Let's say, for example, that you want to improve the model from
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

A corresponding ``translation.py`` file in this application would look like::

    from modeltranslation.translator import translator, TranslationOptions
    from .models import Author, Book

    class TranslatedAuthor(TranslationOptions):
        fields = ('trivia',)

    class TranslatedBook(TranslationOptions):
        fields = ('title',)

    translator.register(Author, TranslatedAuthor)
    translator.register(Book, TranslatedBook)

Note how, in this case, ``mezzanine.pages.translation.TranslatedPage`` is not
referenced in any way. This is due to the fact that
``mezzanine.pages.models.Page`` is not abstract and thus has its own table in
the database. Its fields have already been registered for translation and
modeltranslation will happily handle it for you.

If you want to extend an abstract model, such as
``mezzanine.core.models.Slugged`` or ``mezzanine.core.models.Displayable``,
however you will have to subclass their translation registration. The
``mezzanine.blog`` application makes use of this in its ``translation.py``::

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

Even though you don't add translatable fields in your model beside those
already defined inside mezzanine's models, you have to extends from
``mezzanine.core.translation`` classes so modeltranslation is aware of the
abstract fields it will have to manage.

After that, you can ``manage.py createdb`` for a new project or ``manage.py
sync_translation_fields`` and then ``manage.py update_translation_fields`` for
an existing one.

Enabling Translation for Injected Fields
========================================

If you added some fields in mezzanine's models through ``EXTRA_MODEL_FIELDS``
and want to translate them, you will have to create a custom application that
will hold the necessary ``translation.py`` file.

Adding a translation field to all of mezzanine's content type would look like::

  EXTRA_MODEL_FIELDS = (
      (
          "mezzanine.pages.models.Page.quote",
          "TextField",
          ("Page's Quote",),
          {"blank": True},
      ),
  )

The application containing the corresponding ``translation.py`` file should be
defined *after* ``mezzanine.pages`` in ``INSTALLED_APPS`` but *before* any
application that contains models that subclass ``mezzanine.pages.models.Page``
(such as ``mezzanine.forms``, ``mezzanine.galleries`` or ``cartridge.shop``).
The ``translation.py`` file itself would be::

    from modeltranslation.translator import translator
    from mezzanine.pages.translation import TranslatedPage
    from mezzanine.pages.models import Page

    class TranslatedInjectedPage(TranslatedPage):
        field = ('quote',),

    translator.unregister(Page)
    translator.register(Page, TranslatedInjectedPage)

Redistribuable Applications for Mezzanine
=========================================

If you want to provide translation support for your mezzanine application,
make sure it works with both ``USE_MODELTRANSLATION`` set to ``True`` or
``False``. Mezzanine enforces its value to ``False`` if django-modeltranslation
is not properly installed. Thus it is reliable to check against this setting
when extra steps are required (such as saving an instance of a model in every
languages). In cases of a project with ``USE_MODELTRANSLATION`` set to
``False``, the ``translation.py`` file will just be ignored.

The ``USE_MODELTRANSLATION`` setting is also availlable in the template's
``settings`` dictionnary. Have a look at the
``includes/language_selector.html`` template in ``mezzanine.core`` for a
working example.
