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
via ``mezzanine.pages.admin.PageAdmin``. When creating new pages in the 
admin with a default Mezzanine project, the ``Page`` model is used which 
simply contains a WYSIWYG editable field for content.

.. _creating-custom-content-types:

Creating Custom Content Types
=============================

In order to handle different types of pages that require more structured 
content than provided by the ``Page`` model, you can simply create your 
own models that inherit from ``Page``. For example if we wanted to have 
pages that were photo galleries::

    from django.db import models
    from mezzanine.pages.models import Page

    # The members of Page will be inherited by the Gallery model, such as 
    # title, slug, WYSIWYG content, etc. In this example the Gallery model is 
    # essentially a container for GalleryImage instances.
    class Gallery(Page):
        pass 
        
    class GalleryImage(models.Model):
        gallery = models.ForeignKey("Gallery")
        image = models.ImageField(upload_to="galleries")

You'll also need to create an admin class for the Gallery model that 
inherits from ``mezzanine.pages.admin.PageAdmin``::

    from django.contrib import admin 
    from mezzanine.pages.admin import PageAdmin
    from models import Gallery, GalleryImage

    class GalleryAdmin(PageAdmin):
        inlines = (GalleryImageInline,)
        
    class GalleryImageInline(admin.TabularInline):
        model = GalleryImage
        
    admin.site.register(Gallery, GalleryAdmin)

By using an admin class that inherits from ``PageAdmin`` the admin class 
won't be listed in the admin index page, instead being made available as 
a type of ``Page`` when creating new pages from the navigation tree.

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

The ``Page`` model also contains the method ``Page.get_content_model`` for 
retrieving the custom instance without knowing its type beforehand::

    >>> page.get_content_model() 
    <Gallery: My gallery>

The view function ``mezzanine.pages.views.page`` handles returning a 
``Page`` instance to a template. By default the template ``pages/page.html`` 
is used, but if a custom template exists it will be used instead. The check 
for a custom template will first check for a template with the same name as 
the ``Page`` instance's slug, and if not then a template with a name derived 
from the subclass model's name is checked for. So given the above example 
the templates ``pages/my-gallery.html`` and ``pages/gallery.html`` would be 
checked for respectively.

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

The ``Displayable`` Model
=========================

The abstract model ``mezzanine.core.models.Displayable`` and associated 
manager ``mezzanine.core.managers.PublishedManager`` provide common features 
for items that can be displayed on the site with their own URLs (also known 
as slugs). Some of these features are:

  * Fields for title and WYSIWYG edited content.
  * Auto-generated slug from the title.
  * Draft/published status with the ability to preview drafts.
  * Pre-dated publishing.
  * Meta data.

Content models that do not inherit from the ``Page`` model described earlier 
should inherit from the ``Displayable`` model if any of the above features 
are required. An example of this can be found in the ``mezzanine.blog`` 
application, where ``Blo============gPost`` instances contain their own URLs and views 
that fall outside of the regular URL/view structure of the ``Page`` model.

