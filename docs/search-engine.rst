=============
Search Engine
=============

Mezzanine comes with a built-in search engine that allows site visitors to
search across different types of content. The following section describes
how to programmatically interact with the search engine, how to customize
the way the search engine accesses different types of content, and how
search queries are broken down and used to query models for results.

Search API
==========

The main search API is provided by
``mezzanine.core.managers.SearchableManager``. This is a Django model
manager that provides a custom ``search`` method. Adding search
functionality to any model is as simple as using the ``SearchableManager``
as a manager for your model.

.. note::

    By following the previous example outlined in
    :ref:`creating-custom-content-types` no extra work is required to have
    your custom content included in search queries, as the default search
    functionality in Mezzanine (defined in ``mezzanine.core.views.search``)
    automatically covers any models that inherit from
    ``mezzanine.pages.models.Page`` or ``mezzanine.core.models.Displayable``.

In its most simple form, the ``search`` method takes a single string
argument containing a search query and returns a Django queryset
representing the results. For example, to search for all pages using the
term **plans prices projects**::

    from mezzanine.pages.models import Page

    results = Page.objects.search("plans prices projects")

It's also possible to explicitly control which fields will be used for the
search. For example to search ``Page.title`` and ``Page.content`` only::

    from mezzanine.pages.models import Page

    query = "plans prices projects"
    search_fields = ("title", "content")
    results = Page.objects.search(query, search_fields=search_fields)

If ``search_fields`` is not provided in the call to ``search``, the fields
used will be the default fields specified for the model. These are specified
by providing a ``search_fields`` attribute on any model that uses the
``SearchableManager``. For example, if we wanted to add search capabilities
to our ``GalleryImage`` model from the previous example in
:ref:`creating-custom-content-types`::

    from django.db import models
    from mezzanine.pages.models import Page
    from mezzanine.core.managers import SearchableManager

    class Gallery(Page):
        pass

    # Added the title and description fields here for the search example.
    class GalleryImage(models.Model):
        gallery = models.ForeignKey("Gallery")
        title = models.CharField("Title", max_length=100)
        description = models.CharField("Description", max_length=1000)
        image = models.ImageField(upload_to="galleries")

        objects = SearchableManager()
        search_fields = ("title", "description")

If ``search_fields`` are not specified using any of the approaches above,
then all ``CharField`` and ``TextField`` fields defined on the model are
used.

Ordering Results
================

By default, results are ordered by the number of matches found within the
fields searched. It is possible to control the relative weight of a match
found within one field over a match found in another field. Given the first
example of searching ``Page`` instances, you might decide that a match
within the ``title`` field is worth 5 times as much as a match in the
``description`` field. These relative weights can be defined in the same
fashion as outlined above for defining the fields to be used in a search by
using a slightly different format for the ``search_fields`` argument::

    from mezzanine.pages.models import Page

    query = "plans prices projects"
    search_fields = {"title": 5, "content": 1}
    results = Page.objects.search(query, search_fields=search_fields)

As shown, a dictionary or mapping sequence can be used to associate weights
to fields in any of the cases described above where ``search_fields`` can
be defined.

Searching Heterogeneous Models
==============================

So far we've looked at how to search across a single model, but what if we
want to search across different types of models at once? This is possible
through the use of abstract models. ``SearchableManager`` is designed so
that if it is accessed directly through an abstract model, it will search
across every model that subclasses the abstract model. This makes it
possible to group together different types of models for the purpose of
combined search. Continuing on from our ``GalleryImage`` example, suppose
we also have a ``Document`` model containing files uploaded and that we
wanted a combined search across these models which could both be
conceptually defined as assets. We would then go ahead and create an
abstract model called ``Asset`` for the sake of grouping these together
for search::

    class Asset(models.Model):
        title = models.CharField("Title", max_length=100)
        description = models.CharField("Title", max_length=1000)

        objects = SearchableManager()
        search_fields = ("title", "description")

        class Meta:
            abstract = True

    class GalleryImage(Asset):
        gallery = models.ForeignKey("Gallery")
        image = models.ImageField(upload_to="galleries")

    class Document(Asset):
        image = models.FileField(upload_to="documents")

By accessing ``SearchableManager`` directly via the ``Asset`` abstract model
we can search across the ``GalleryImage`` and ``Document`` models at once::

    >>> Asset.objects.search("My")
    [<GalleryImage: My Image 1>, <Document: My Doc>, <GalleryImage: My Image 2>]

.. note::

    It was mentioned earlier that the ``search`` method returns a Django
    queryset meaning that you can then chain together further queryset
    methods onto the result. However when searching across heterogeneous
    models via an abstract model, this is not the case and the result is a
    list of model instances.

Query Behaviour
===============

When a call to ``SearchableManager.search`` is performed, the query entered
is processed through several steps until it is translated into a Django
queryset. By default the query is broken up into keywords, so the query
**plans prices projects** would return results that contain any of the words
**plans** or **prices** or **projects**.

The query can contain several special operators which allow for this
behaviour to be controlled further. Quotes around exact phrases will
ensure that the phrase is searched for specifically, for example the query
**"plans prices" projects** will return results matching the exact phrase
**plans prices** or the word **projects**, in contrast to the previous
example.

You can also prefix both words and phrases with + or - symbols. The +
symbol will ensure the word or phrase is contained in all results, and the
- symbol will ensure that no results will be returned containing the word
or phrase. For example the query **+"plans prices" -projects** would return
results that must contain the phrase **plans prices** and must not contain
the word **projects**.

Once the query has been parsed into words and phrases to be included or
excluded, a second step is performed where the query is stripped of common
words know as **stop words**. These are common words such as **and**,
**the** or **like** that are generally not meaningful and cause irrelevant
results to be returned. The list of stop words is stored in the setting
``STOP_WORDS`` as described in the :doc:`configuration` section.
