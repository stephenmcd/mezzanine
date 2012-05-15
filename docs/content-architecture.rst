====================
Content Architecture
====================

Mezzanine primarily revolves around the models found in two packages,
``mezzanine.core`` and ``mezzanine.pages``. This section describes these
models and how to extend them to create your own custom content for a
Mezzanine site.

The ``Page`` Model
==================

The foundation of a Mezzanine site is the model
``mezzanine.pages.models.Page``. Each ``Page`` instance is stored in a
hierarchical tree to form the site's navigation, and an interface for
managing the structure of the navigation tree is provided in the admin
via ``mezzanine.pages.admin.PageAdmin``. All types of content inherit from
the ``Page`` model and Mezzanine provides a default content type via the
``mezzanine.pages.models.RichTextPage`` model which simply contains a WYSIWYG
editable field for managing content.

.. _creating-custom-content-types:

Creating Custom Content Types
=============================

In order to handle different types of pages that require more structured
content than provided by the ``RichTextPage`` model, you can simply create
your own models that inherit from ``Page``. For example if we wanted to have
pages that were photo galleries::

    from django.db import models
    from mezzanine.pages.models import Page

    # The members of Page will be inherited by the Gallery model, such as
    # title, slug, etc. In this example the Gallery model is essentially a
    # container for GalleryImage instances.
    class Gallery(Page):
        notes = models.TextField("Notes")

    class GalleryImage(models.Model):
        gallery = models.ForeignKey("Gallery")
        image = models.ImageField(upload_to="galleries")

Next you'll need to register your model with Django's admin to make it
available as a content type. If your content type only exposes some new
fields that you'd like to make editable in the admin, you can simply
register your model using the ``mezzanine.pages.admin.PageAdmin`` class::

    from django.contrib import admin
    from mezzanine.pages.admin import PageAdmin
    from models import Gallery

    admin.site.register(Gallery, PageAdmin)

Any regular model fields on your content type will be available when adding
or changing an instance of it in the admin. This is similar to Django's
behaviour when registering models in the admin without using an
admin class, or when using an admin class without fieldsets defined. In these
cases all the fields on the model are available in the admin.

If however you need to customize your admin class, you can inherit from
``PageAdmin`` and implement your own admin class. The only difference is
that you'll need to take a copy of ``PageAdmin.fieldsets`` and modify it
if you want to implement your own fieldsets, otherwise you'll lose the fields
that the ``Page`` model implements::

    from copy import deepcopy
    from django.contrib import admin
    from mezzanine.pages.admin import PageAdmin
    from models import Gallery, GalleryImage

    gallery_extra_fieldsets = ((None, {"fields": ("notes",)}),)

    class GalleryImageInline(admin.TabularInline):
        model = GalleryImage

    class GalleryAdmin(PageAdmin):
        inlines = (GalleryImageInline,)
        fieldsets = deepcopy(PageAdmin.fieldsets) + gallery_extra_fieldsets

    admin.site.register(Gallery, GalleryAdmin)

When registering content type models with ``PageAdmin`` or subclasses of
it, the admin class won't be listed in the admin index page, instead being
made available as a type of ``Page`` when creating new pages from the
navigation tree.

.. note::

    When creating custom content types, you must inherit directly from
    the ``Page`` model. Further levels of subclassing are currently not
    supported. Therefore you cannot subclass the ``RichTextPage`` or
    any other custom content types you create yourself. Should you need
    to implement a WYSIWYG editable field in the way the ``RichTextPage``
    model does, you can simply subclass both ``Page`` and ``RichText``,
    the latter being imported from ``mezzanine.core.models``.

Page Permissions
================

The navigation tree in the admin where pages are managed will take
into account any permissions defined using `Django's permission system
<http://docs.djangoproject.com/en/dev/topics/auth/#permissions>`_. For
example if a logged in user doesn't have permission to add new
instances of the ``Gallery`` model from our previous example, it won't
be listed in the types of pages that user can add when viewing the
navigation tree in the admin.

In conjunction with Django's permission system, the ``Page`` model also
implements the methods ``can_add``, ``can_change`` and ``can_delete``.
These methods provide a way for custom page types to implement their
own permissions by being overridden on subclasses of the ``Page`` model.

Each of these methods takes a single argument which is the current
request object. This provides the ability to define custom permission
methods with access to the current user as well.

.. note::

    The ``can_add`` permission in the context of an existing page has
    a different meaning than in the context of an overall model as is
    the case with Django's permission system. In the case of a page
    instance, ``can_add`` refers to the ability to add child pages.

For example, if our ``Gallery`` content type should only contain one
child page at most, and only be deletable when added as a child page
(unless you're a superuser), the following permission methodss could
be implemented::

    class Gallery(Page):
        notes = models.TextField("Notes")

        def can_add(self, request):
            return self.children.count() == 0

        def can_delete(self, request):
            return request.user.is_superuser or self.parent is not None

Displaying Custom Content Types
===============================

When creating models that inherit from the ``Page`` model, multi-table
inheritance is used under the hood. This means that when dealing with the
page object, an attribute is created from the subclass model's name. So
given a ``Page`` instance using the previous example, accessing the
``Gallery`` instance would be as follows::

    >>> Gallery.objects.create(title="My gallery")
    <Gallery: My gallery>
    >>> page = Page.objects.get(title="My gallery")
    >>> page.gallery
    <Gallery: My gallery>

And in a template::

    <h1>{{ page.gallery.title }}</h1>
    <p>{{ page.gallery.notes }}</p>
    {% for galleryimage in page.gallery.galleryimage_set.all %}
    <img src="{{ MEDIA_URL }}{{ galleryimage.image }}" />
    {% endfor %}

The ``Page`` model also contains the method ``Page.get_content_model`` for
retrieving the custom instance without knowing its type beforehand::

    >>> page.get_content_model()
    <Gallery: My gallery>

Page Templates
==============

The view function ``mezzanine.pages.views.page`` handles returning a
``Page`` instance to a template. By default the template ``pages/page.html``
is used, but if a custom template exists it will be used instead. The check
for a custom template will first check for a template with the same name as
the ``Page`` instance's slug, and if not then a template with a name derived
from the subclass model's name is checked for. So given the above example
the templates ``pages/my-gallery.html`` and ``pages/gallery.html`` would be
checked for respectively.

Overriding vs Extending Templates
=================================

A typical problem that reusable Django apps face, is being able to
extend the app's templates rather than overriding them. The app will
usually provide templates that the app will look for by name, which
allows the developer to create their own versions of the templates in
their project's templates directory. However if the template is
sufficiently complex, with a good range of extendable template blocks,
they need to duplicate all of the features of the template within
their own version. This may cause the project's version of the
templates to become incompatible as new versions of the upstream app
become available.

Ideally we would be able to use Django's ``extends`` tag to extend the
app's template instead, and only override the template blocks we're
interested in. The problem with this however, is that the app will
attempt to load the template with a specific name, so we can't override
*and* extend a template at the same time, as circular inheritance will
occur, eg Django thinks the template is trying to extend itself, which
is impossible.

To solve this problem, Mezzanine provides the ``overextends`` template
tag, which allows you to extend a template with the same name. The
``overextends`` tag works the same way as Django's ``extends`` tag, (in
fact it subclasses it), so it must be the first tag in the template.
What it does differently is that the template using it will be excluded
from loading when Django searches for the template to extend from.

Page Processors
===============

So far we've covered how to create and display custom types of pages, but
what if we want to extend them further with more advanced features? For
example adding a form to the page and handling when a user submits the form.
This type of logic would typically go into a view function, but since every
``Page`` instance is handled via the view function
``mezzanine.pages.views.page`` we can't create our own views for pages.
Mezzanine solves this problem using *Page Processors*.

*Page Processors* are simply functions that can be associated to any custom
``Page`` models and are then called inside the
``mezzanine.pages.views.page`` view when viewing the associated ``Page``
instance. A Page Processor will always be passed two arguments - the request
and the ``Page`` instance, and can either return a dictionary that will be
added to the template context, or it can return any of Django's
``HttpResponse`` classes which will override the
``mezzanine.pages.views.page`` view entirely.

To associate a Page Processor to a custom ``Page`` model you must create the
function for it in a module called ``page_processors.py`` inside one of your
``INSTALLED_APPS`` and decorate it using the decorator
``mezzanine.pages.page_processors.processor_for``.

Continuing on from our gallery example, suppose we want to add an enquiry
form to each gallery page. Our ``page_processors.py`` module in the gallery
app would be as follows::

    from django import forms
    from django.http import HttpResponseRedirect
    from mezzanine.pages.page_processors import processor_for
    from models import Gallery

    class GalleryForm(forms.Form):
        name = forms.CharField()
        email = forms.EmailField()

    @processor_for(Gallery)
    def gallery_form(request, page):
        form = GalleryForm()
        if request.method == "POST":
            form = GalleryForm(request.POST)
            if form.is_valid():
                # Form processing goes here.
                redirect = request.path + "?submitted=true"
                return HttpResponseRedirect(redirect)
        return {"form": form}

The ``processor_for`` decorator can also be given a ``slug`` argument rather
than a Page subclass. In this case the Page Processor will be run when the
exact slug matches the page being viewed.

Non-Page Content
================

Sometimes you might need to use regular Django applications within your
site, that fall outside of Mezzanine's page structure. Mezzanine fully
supports using regular Django applications. All you need to do is add
the app's urlpatterns to your project's ``urls.py`` module. Mezzanine's
blog application for example, does not use ``Page`` content types, and
is just a regular Django app.

Mezzanine provides some helpers for your Django apps to integrate more
closely with Mezzanine.

The ``Displayable`` Model
-------------------------

The abstract model ``mezzanine.core.models.Displayable`` and associated
manager ``mezzanine.core.managers.PublishedManager`` provide common features
for items that can be displayed on the site with their own URLs (also known
as slugs). Mezzanine's ``Page`` model subclasses it. Some of its features are:

  * Meta data such as a title, description and keywords.
  * Auto-generated slug from the title.
  * Draft/published status with the ability to preview drafts.
  * Pre-dated publishing.
  * Searchable by Mezzanine's :doc:`search-engine`.

Models that do not inherit from the ``Page`` model described earlier
should subclass the ``Displayable`` model if any of the above features
are required. An example of this can be found in the ``mezzanine.blog``
application, where ``BlogPost`` instances contain their own URLs and views
that fall outside of the regular URL/view structure of the ``Page`` model.

Navigation Integration
----------------------

A common requirement when using regular Django apps with Mezzanine is for
pages in the site's navigation to point to the urlpatterns for the app.
Implementing this simply requires creating a page with a URL used by the
application.

First create a page via the page tree in the admin, and enter the correct
URL (under the Meta data section) that maps to the urlpattern in your
Django app. This page will then be marked as *protected*, which means it
can't be deleted via the admin, nor can its URL be changed in the admin,
since it points to a separate Django app.

The second optional step, is to wrap the application's views in the
``mezzanine.pages.decorators.for_page`` decorator. This will add the page
instance to the context variable named ``page``, so the title, description,
and any specific fields for the content type that you chose to use when
creating the page, will be available in the template that gets loaded. The
``for_page`` decorator takes a single argument, the URL for the page that
the view should include. For example, here's the start of the view that
lists blog posts in Mezzanine's blog application::

    from mezzanine.pages.decorators import for_page

    @for_page(settings.BLOG_SLUG)
    def blog_post_list(request, tag=None, year=None, month=None, username=None,
                       category=None, template="blog/blog_post_list.html"):
        # Regular Django view code from this point on.
