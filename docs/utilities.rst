
=========
Utilities
=========

The following section documents general utilities available with
Mezzanine. While these aren't a core part of Mezzanine itself,
they're widely used across many areas of Mezzanine, and can be very
useful in conjunction with your own custom content and features.

Firstly covered are the utilities found in the ``mezzanine.generic``
app, such as :ref:`keywords`, :ref:`comments`, and :ref:`ratings`.
Each of these form a common pattern:

  * A model is provided containing generic relationships using
    Django's `django.contrib.contenttypes <https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/>`_ app
  * A custom model field is provided for defining relationships to the
    ``mezzanine.generic`` model, which can then be applied to any of
    your own models
  * The custom field injects extra fields onto your model, with
    de-normalized data populated on save
  * Template tags are provided for displaying the related data, forms
    for posting them, and views for handling form posts where
    applicable

For a complete implementation reference, take a look at the built-in
blog app ``mezzanine.blog`` which makes use of all these.

Lastly, some of the :ref:`templatetags` found within
``mezzanine.core.templatetags.mezzanine_tags`` are covered.

.. _keywords:

Keywords
========

Keywords provided by the ``mezzanine.generic`` app are pervasive
throughout Mezzanine. They're assigned to both the ``Page`` model and
the ``Displayable`` model from which it's derived. Given that these
models form the foundation of most content within Mezzanine, more often
than not you're dealing with models that are already using keywords.

Suppose we have a regular Django model though, such as our ``Book``
example from the previous example in :doc:`content-architecture`::

    from django.db import models
    from mezzanine.generic.fields import KeywordsField

    class Book(models.Model):
        author = models.ForeignKey("Author")
        cover = models.ImageField(upload_to="authors")
        keywords = KeywordsField()

When editing ``Book`` instances in the admin, we'll now be able to
choose keywords from the pool of keywords used throughout the site,
and also assign new keywords if needed. We can then easily query for
books given any keywords::

    Book.objects.filter(keywords__keyword__title__in=["eggs", "ham"])

Given a ``Book`` instance in a template, we can also display the book's
keywords using the ``keywords_for`` template tag, which will inject
a list of keywords into the template, using the ``as var_name`` variable
name argument supplied to it::

    {% load keyword_tags %}

    {% keywords_for book as keywords %}
    {% if keywords %}
    <ul>
        <li>Keywords:</li>
        {% for keyword in keywords %}
        <li><a href="{% url "books_for_keyword" keyword.slug %}">{{ keyword }}</a></li>
        {% endfor %}
    </ul>
    {% endif %}

You'll see here each ``Keyword`` instance has a slug field - we use it
in a fictitious urlpattern called ``books_for_keyword``, which could
then retrieve books for a given keyword by slug::

    Book.objects.filter(keywords__keyword__slug=slug)

Any model with a ``KeywordsField`` field assigned to it will have a
``FIELD_NAME_string`` field assigned to it, where ``FIELD_NAME`` is the
name given to the ``KeywordsField`` attribute on your model, which
would be ``Book.keywords_string`` in the above example. Each time
keywords change, the ``keywords_string`` field is populated with a
comma separated string list of each of the keywords. This can be used
in conjunction with Mezzanine's :doc:`search-engine` - behavior that is
provided by default for the ``Page`` and ``Displayable`` models.

.. _comments:

Threaded Comments
=================

Threaded comments provided by the ``mezzanine.generic`` app are an
extension of Django's `django_comments
<https://github.com/django/django-contrib-comments>`_ app.
Mezzanine's threaded comments fundamentally extend Django's comments
to allow for threaded conversations, where comments can be made in
reply to other comments.

Again as with our ``Book`` example, suppose we wanted to added threaded
conversations to our book pages in templates, we first define comments
on the ``Book`` model::

    from django.db import models
    from mezzanine.generic.fields import CommentsField

    class Book(models.Model):
        author = models.ForeignKey("Author")
        cover = models.ImageField(upload_to="authors")
        comments = CommentsField()

Then given a ``Book`` instance named ``book`` in a template::

    {% load comment_tags %}

    <h3>There are {{ book.comments_count }} comment{{ book.comments_count|pluralize }}</h3>
    {% comments_for book %}

The ``comments_for`` template tag is a Django `inclusion tag
<https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#howto-custom-template-tags-inclusion-tags>`_,
that includes the template ``generic/includes/comments.html``, which
recursively includes the template ``generic/includes/comment.html`` to
build up the threaded conversation. To customize the look and feel of
the threaded conversation, simply override these templates in your
project.

As you can see in the template example we have a
``Book.comments_count`` field injected onto our ``Book`` model. This
works the same way as described above for the ``KeywordsField``, where
the name is derived from the name given to the ``CommentsField``
attribute on the model, and updated each time the number of comments
change.

You can also require that users must be logged in to comment. This is
controlled by setting the ``COMMENTS_ACCOUNT_REQUIRED`` setting to
``True``. In this case, the comment form will still be displayed, but
on submitting a comment, the user will be redirected to the
login/signup page, where after logging in, their comment will be posted
without having to re-submit it. See the :doc:`user-accounts` section
for full details on configuring public user accounts in Mezzanine.

.. _ratings:

Ratings
=======

The ratings provided by the ``mezzanine.generic`` app allow people to
give a rating for any model that has ratings set up. Suppose we wanted
to allow people to rate our books from 1 to 10, first we define what
the rating range is via the ``RATINGS_RANGE`` setting::

    RATINGS_RANGE = range(1, 11)

And then add ratings to our ``Book`` model::

    from django.db import models
    from mezzanine.generic.fields import RatingField

    class Book(models.Model):
        author = models.ForeignKey("Author")
        cover = models.ImageField(upload_to="authors")
        rating = RatingField()

And then in our book template::

    {% load rating_tags %}

    {% rating_for book %}

The ``rating_for`` template tag is another inclusion tag, which uses
the template ``generic/includes/rating.html``. It simply displays the
current average rating, and a form with radio buttons for rating. You
may wish to customize this and use visual icons, like stars, for the
ratings.

Like the other custom fields in ``mezzanine.generic``, the
``RatingField`` will inject fields derived from its attribute name
onto the model which it's assigned to, which are updated when a new
rating is made. Given our ``Book`` example, the ``RatingField`` would
inject:

  * ``Book.rating_average`` - average rating
  * ``Book.rating_sum`` - total sum of all ratings
  * ``Book.rating_count`` - total count of all ratings

Like threaded comments, ratings can be limited to authenticated users
by setting the ``RATINGS_ACCOUNT_REQUIRED`` setting to ``True``.

.. _templatetags:

General Template Tags
=====================

Following are some template tags defined in
``mezzanine.core.templatetags.mezzanine_tags`` - they're general
purpose and can be used across a variety of scenarios.

``fields_for``
--------------

The ``fields_for`` template tag is an inclusion tag that takes a form
object as its single argument, and renders the fields for the form. It
uses the template ``core/templates/form_fields.html``, which can then
be overridden to customize the look and feel of all forms throughout a
Mezzanine site::

    {% load mezzanine_tags %}

    <form method="POST">
        {% fields_for some_form_object %}
        <input type="submit">
    </form>

``sort_by``
-----------

The ``sort_by`` template tag is a general sorting utility. It's a
filter tag similar to Django's
`dictsort <https://docs.djangoproject.com/en/dev/ref/templates/builtins/#std:templatefilter-dictsort>`_
filter tag, but instead of only accepting sequences of dicts and a key
name, it also accepts sequences of objects and an attribute name,
making it much more general purpose.

Here's an example with the ``keywords_for`` tag described above, which
assigns an ``item_count`` attribute to each keyword returned to the
template::

    {% load mezzanine_tags keywords_tags %}

    {% keywords_for book as keywords %}
    {% for keyword in keywords|sort_by:"item_count" %}
    ... etc ...
    {% endfor %}

``thumbnail``
-------------

The ``thumbnail`` template tag provides on-the-fly image resizing. It
takes the relative path to the image file to resize, and mandatory width
and height arguments.

When the ``thumbnail`` template tag is called for a given set of
arguments the first time, the thumbnail is generated and its relative
path is returned. Subsequent calls with the same arguments will return
the same thumbnail path, without resizing it again, so resizes only
occur when first requested.

Given our book example's ``Book.cover`` field, suppose we wanted
to render cover thumbnails with a 100 pixel width, and proportional
height::

    {% load mezzanine_tags %}

    <img src="{{ MEDIA_URL }}{% thumbnail book.cover 100 0 %}">

The ``thumbnail`` template tag also accepts several other optional
arguments for controlling the generated thumbnail:

  * ``upscale`` - A boolean controlling whether the thumbnail should
     grow beyond its original size when resizing (defaults to True)
  * ``quality`` - A value from 0 to 100 controlling the JPG quality
    (defaults to 95)
  * ``left`` and ``top`` - Values from 0 to 1 controlling where the
    image will be cropped (each defaults to 0.5, namely the center)
  * ``padding`` - A boolean controlling whether the thumbnail will
    be padded rather than cropped (defaults to False)
  * ``padding_color`` - RGB string controlling the background color
    when ``padding`` is True (defaults to "#fff")
