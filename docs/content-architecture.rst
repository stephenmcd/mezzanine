====================
Content Architecture
====================

Mezzanine primarily revolves around the models found in two packages,
``mezzanine.core`` and ``mezzanine.pages``. This section describes
these models and how to extend them to create your own custom content
for a Mezzanine site.

The ``Page`` Model
==================

The foundation of a Mezzanine site is the model
``mezzanine.pages.models.Page``. Each ``Page`` instance is stored in a
hierarchical tree to form the site's navigation, and an interface for
managing the structure of the navigation tree is provided in the admin
via ``mezzanine.pages.admin.PageAdmin``. All types of content inherit
from the ``Page`` model and Mezzanine provides a default content type
via the ``mezzanine.pages.models.RichTextPage`` model which simply
contains a WYSIWYG editable field for managing HTML content.

.. _creating-custom-content-types:

Creating Custom Content Types
=============================

In order to handle different types of pages that require more
structured content than provided by the ``RichTextPage`` model, you can
simply create your own models that inherit from ``Page``. For example
if we wanted to have pages that were authors with books::

    from django.db import models
    from mezzanine.pages.models import Page

    # The members of Page will be inherited by the Author model, such
    # as title, slug, etc. For authors we can use the title field to
    # store the author's name. For our model definition, we just add
    # any extra fields that aren't part of the Page model, in this
    # case, date of birth.

    class Author(Page):
        dob = models.DateField("Date of birth")

    class Book(models.Model):
        author = models.ForeignKey("Author")
        cover = models.ImageField(upload_to="authors")

Next you'll need to register your model with Django's admin to make it
available as a content type. If your content type only exposes some new
fields that you'd like to make editable in the admin, you can simply
register your model using the ``mezzanine.pages.admin.PageAdmin``
class::

    from django.contrib import admin
    from mezzanine.pages.admin import PageAdmin
    from .models import Author

    admin.site.register(Author, PageAdmin)

Any regular model fields on your content type will be available when
adding or changing an instance of it in the admin. This is similar to
Django's behaviour when registering models in the admin without using
an admin class, or when using an admin class without fieldsets defined.
In these cases all the fields on the model are available in the admin.

If however you need to customize your admin class, you can inherit from
``PageAdmin`` and implement your own admin class. The only difference
is that you'll need to take a copy of ``PageAdmin.fieldsets`` and
modify it if you want to implement your own fieldsets, otherwise you'll
lose the fields that the ``Page`` model implements::

    from copy import deepcopy
    from django.contrib import admin
    from mezzanine.pages.admin import PageAdmin
    from .models import Author, Book

    author_extra_fieldsets = ((None, {"fields": ("dob",)}),)

    class BookInline(admin.TabularInline):
        model = Book

    class AuthorAdmin(PageAdmin):
        inlines = (BookInline,)
        fieldsets = deepcopy(PageAdmin.fieldsets) + author_extra_fieldsets

    admin.site.register(Author, AuthorAdmin)

When registering content type models with ``PageAdmin`` or subclasses
of it, the admin class won't be listed in the admin index page, instead
being made available as a type of ``Page`` when creating new pages from
the navigation tree.

.. note::

    When creating custom content types, you must inherit directly from
    the ``Page`` model. Further levels of subclassing are currently not
    supported. Therefore you cannot subclass the ``RichTextPage`` or
    any other custom content types you create yourself. Should you need
    to implement a WYSIWYG editable field in the way the
    ``RichTextPage`` model does, you can simply subclass both ``Page``
    and ``RichText``, the latter being imported from
    ``mezzanine.core.models``.

Displaying Custom Content Types
===============================

When creating models that inherit from the ``Page`` model, multi-table
inheritance is used under the hood. This means that when dealing with
the page object, an attribute is created from the subclass model's
name. So given a ``Page`` instance using the previous example,
accessing the ``Author`` instance would be as follows::

    >>> Author.objects.create(title="Dr Seuss")
    <Author: Dr Seuss>
    >>> page = Page.objects.get(title="Dr Seuss")
    >>> page.author
    <Author: Dr Seuss>

And in a template::

    <h1>{{ page.author.title }}</h1>
    <p>{{ page.author.dob }}</p>
    {% for book in page.author.book_set.all %}
    <img src="{{ MEDIA_URL }}{{ book.cover }}">
    {% endfor %}

The ``Page`` model also contains the method ``Page.get_content_model``
for retrieving the custom instance without knowing its type::

    >>> page.get_content_model()
    <Author: Dr Seuss>

Page Templates
==============

The view function ``mezzanine.pages.views.page`` handles returning a
``Page`` instance to a template. By default the template
``pages/page.html`` is used, but if a custom template exists it will be
used instead. The check for a custom template will first check for a
template with the same name as the ``Page`` instance's slug, and if not
then a template with a name derived from the subclass model's name is
checked for. So given the above example the templates
``pages/dr-seuss.html`` and ``pages/author.html`` would be checked for
respectively.

The view function further looks through the parent hierarchy of the ``Page``.
If a ``Page`` instance with slug ``authors/dr-seuss`` is a child of the
``Page`` with slug ``authors``, the templates ``pages/authors/dr-seuss.html``,
``pages/authors/dr-seuss/author.html``, ``pages/authors/author.html``,
``pages/author.html``, and ``pages/page.html`` would be checked for
respectively. This lets you specify a template for all children of a ``Page``
and a different template for the ``Page`` itself. For example, if an
additional author were added as a child page of ``authors/dr-seuss`` with the
slug ``authors/dr-seuss/theo-lesieg``, the template
``pages/authors/dr-seuss/author.html`` would be among those checked.

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
occur, e.g. Django thinks the template is trying to extend itself, which
is impossible.

To solve this problem, Mezzanine provides the ``overextends`` template
tag, which allows you to extend a template with the same name. The
``overextends`` tag works the same way as Django's ``extends`` tag, (in
fact it subclasses it), so it must be the first tag in the template.
What it does differently is that the template using it will be excluded
from loading when Django searches for the template to extend from.

Page Processors
===============

So far we've covered how to create and display custom types of pages,
but what if we want to extend them further with more advanced features?
For example adding a form to the page and handling when a user submits
the form. This type of logic would typically go into a view function,
but since every ``Page`` instance is handled via the view function
``mezzanine.pages.views.page`` we can't create our own views for pages.
Mezzanine solves this problem using *Page Processors*.

*Page Processors* are simply functions that can be associated to any
custom ``Page`` models and are then called inside the
``mezzanine.pages.views.page`` view when viewing the associated
``Page`` instance. A Page Processor will always be passed two arguments
- the request and the ``Page`` instance, and can either return a
dictionary that will be added to the template context, or it can return
any of Django's ``HttpResponse`` classes which will override the
``mezzanine.pages.views.page`` view entirely.

To associate a Page Processor to a custom ``Page`` model you must
create the function for it in a module called ``page_processors.py``
inside one of your ``INSTALLED_APPS`` and decorate it using the
decorator ``mezzanine.pages.page_processors.processor_for``.

Continuing on from our author example, suppose we want to add an
enquiry form to each author page. Our ``page_processors.py`` module in
the author app would be as follows::

    from django import forms
    from django.http import HttpResponseRedirect
    from mezzanine.pages.page_processors import processor_for
    from .models import Author

    class AuthorForm(forms.Form):
        name = forms.CharField()
        email = forms.EmailField()

    @processor_for(Author)
    def author_form(request, page):
        form = AuthorForm()
        if request.method == "POST":
            form = AuthorForm(request.POST)
            if form.is_valid():
                # Form processing goes here.
                redirect = request.path + "?submitted=true"
                return HttpResponseRedirect(redirect)
        return {"form": form}

The ``processor_for`` decorator can also be given a ``slug`` argument
rather than a Page subclass. In this case the Page Processor will be
run when the exact slug matches the page being viewed.

Page Permissions
================

The navigation tree in the admin where pages are managed will take
into account any permissions defined using `Django's permission system
<http://docs.djangoproject.com/en/dev/topics/auth/#permissions>`_. For
example if a logged in user doesn't have permission to add new
instances of the ``Author`` model from our previous example, it won't
be listed in the types of pages that user can add when viewing the
navigation tree in the admin.

In conjunction with Django's permission system, the ``Page`` model also
implements the methods ``can_add``, ``can_change`` and ``can_delete``.
These methods provide a way for custom page types to implement their
own permissions by being overridden on subclasses of the ``Page``
model.

Each of these methods takes a single argument which is the current
request object. This provides the ability to define custom permission
methods with access to the current user as well.

.. note::

    The ``can_add`` permission in the context of an existing page has
    a different meaning than in the context of an overall model as is
    the case with Django's permission system. In the case of a page
    instance, ``can_add`` refers to the ability to add child pages.

For example, if our ``Author`` content type should only contain one
child page at most, and only be deletable when added as a child page
(unless you're a superuser), the following permission methods could
be implemented::

    class Author(Page):
        dob = models.DateField("Date of birth")

        def can_add(self, request):
            return self.children.count() == 0

        def can_delete(self, request):
            return request.user.is_superuser or self.parent is not None

Page Menus
==========

We've looked closely at the aspects of individual pages, now let's look
at displaying all of the pages as a hierarchical menu. A typical site
may contain several different page menus, for example a menu that shows
primary pages on the header of the site, with secondary pages as
drop-down lists. Another type of menu would be a full or partial tree in
a side-bar on the site. The footer may display a menu with primary and
secondary pages grouped together as vertical lists.

Mezzanine provides the ``page_menu`` template tag for rendering the
above types of page menus, or any other type you can think of. The
``page_menu`` template tag is responsible for rendering a single
branch of the page tree at a time, and accepts two optional arguments
(you'll usually need to supply at least one of them) in either order.
The arguments are the name of a menu template to use for a single branch
within the page tree, and the parent menu item for the branch that will
be rendered.

The page menu template will be provided with a variable ``page_branch``,
which contains a list of pages for the current branch. We can then call
the ``page_menu`` template tag for each page in the branch, using the
page as the parent argument to render its children. When calling the
``page_menu`` template tag from within a menu template, we don't need to
supply the template name again, as it can be inferred. Note that by
omitting the parent page argument for the ``page_menu`` template tag,
the first branch rendered will be all of the primary pages, that is,
all of the pages without a parent.

Here's a simple menu example using two template files, that renders the
entire page tree using unordered list HTML tags::

    <!-- First template: perhaps base.html, or an include file -->
    {% load pages_tags %}
    {% page_menu "pages/menus/my_menu.html" %}

    <!-- Second template: pages/menus/my_menu.html -->
    {% load pages_tags %}
    <ul>
    {% for page in page_branch %}
    <li>
        <a href="{{ page.get_absolute_url }}">{{ page.title }}</a>
        {% page_menu page %}
    </li>
    {% endfor %}
    </ul>

The first file starts off the menu without specifying a parent page so
that primary pages are first rendered, and only passes in the menu
template to use. The second file is the actual menu template that
includes itself recursively for each branch in the menu. We could even
specify a different menu template in the call to ``page_menu`` in our
menu template, if we wanted to use a different layout for child pages.

Filtering Menus
---------------

Each ``Page`` instance has a field ``in_menus`` which specifies which
menus the page should appear in. In the admin interface, the
``in_menus`` field is a list of checkboxes for each of the menu
templates. The menu choices for the ``in_menus`` field are defined by
the ``PAGE_MENU_TEMPLATES`` setting, which is a sequence of menu
templates. Each item in the sequence is a three item sequence,
containing a unique ID for the template, a label for the template, and
the template path. For example in your ``settings.py`` module::

    PAGE_MENU_TEMPLATES = (
        (1, "Top navigation bar", "pages/menus/dropdown.html"),
        (2, "Left-hand tree", "pages/menus/tree.html"),
        (3, "Footer", "pages/menus/footer.html"),
    )

Which of these entries is selected for new pages (all are selected by default)
is controlled by the ``PAGE_MENU_TEMPLATES_DEFAULT`` setting. For example,
``PAGE_MENU_TEMPLATES_DEFAULT = (1, 3)`` will cause the admin section 
to pre-select the "Top navigation bar" and the "Footer" when using 
the example above.

The selections made for the ``in_menus`` field on each page don't
actually filter a page from being included in the ``page_branch``
variable that contains the list of pages for the current branch. Instead
it's used to set the value of ``page.in_menu`` for each page in the
menu template, so it's up to your menu template to check the page's
``in_menu`` attribute explicitly, in order to exclude it::

    <!-- Second template again, with in_menu support -->
    {% load pages_tags %}
    <ul>
    {% for page in page_branch %}
    {% if page.in_menu %}
    <li>
        <a href="{{ page.get_absolute_url }}">{{ page.title }}</a>
        {% page_menu page %}
    </li>
    {% endif %}
    {% endfor %}
    </ul>

Note that if a menu template is not defined in the
``PAGE_MENU_TEMPLATES`` setting, the branch pages supplied to it will
always have the ``in_menu`` attribute set to ``True``, so the only way
this will be ``False`` is if the menu template has been added to
``PAGE_MENU_TEMPLATES``, and then *not* selected for a page in the admin
interface.

Menu Variables
--------------

The ``page_menu`` template tag provides a handful of variables, both in
the template context, and assigned to each page in the branch, for
helping you to build advanced menus.

  * ``page_branch`` - a list of pages for the current branch
  * ``on_home`` - a boolean for whether the homepage is being viewed
  * ``has_home`` - a boolean for whether a page object exists for the
    homepage, which is used to check whether a hard-coded link to the
    homepage should be used in the page menu
  * ``branch_level`` - an integer for the current branch depth
  * ``page_branch_in_menu`` - a boolean for whether this branch should
    be in the menu (see "filtering menus" below)
  * ``parent_page`` - a reference to the parent page
  * ``page.in_menu`` - a boolean for whether the branch page should
    be in the menu (see "filtering menus" below)
  * ``page.has_children`` - a boolean for whether the branch page has
    any child pages at all, disregarding the current menu
  * ``page.has_children_in_menu`` - a boolean for whether the branch
    page has any child pages that appear in the current menu
  * ``page.num_children`` - an integer for the number of child pages the
    branch page has in total, disregarding the current menu
  * ``page.num_children_in_menu`` - an integer for the number of child
    pages the branch page has, that also appear in the current menu
  * ``page.is_current_child`` - a boolean for whether the branch page
    is a child of the current page being viewed
  * ``page.is_current_sibling`` - a boolean for whether the branch page
    is a sibling (has the same parent) of the current page being viewed
  * ``page.is_current_parent`` - a boolean for whether the branch page
    is the direct parent of the current page being viewed.
  * ``page.is_current_or_ascendant`` - a boolean for whether the branch
    page is the current page being viewed, or an ascendant (parent,
    grand-parent, etc) of the current page being viewed
  * ``page.is_primary`` - a boolean for whether the branch page
    is a primary page (has no parent)
  * ``page.html_id`` - a unique string that can be used as the HTML ID
    attribute
  * ``page.branch_level`` - an integer for the branch page's depth

Here's a commonly requested example of custom menu logic. Suppose you
have primary navigation across the top of the site showing only primary
pages, representing sections of the site. You then want to have a tree
menu in a sidebar, that displays all pages within the section of the
site currently being viewed. To achieve this we recursively move through
the page tree, only drilling down through child pages if
``page.is_current_or_ascendant`` is ``True``, or if the page isn't a
primary page. The key here is the ``page.is_current_or_ascendant``
check is only applied to the primary page, so all of its descendants
end up being rendered. Finally, we also only display the link to each
page if it isn't the primary page for the section::

    {% load pages_tags %}
    <ul>
    {% for page in page_branch %}
    {% if page.in_menu %}
    {% if page.is_current_or_ascendant or not page.is_primary %}
    <li>
        {% if not page.is_primary %}
        <a href="{{ page.get_absolute_url }}">{{ page.title }}</a>
        {% endif %}
        {% page_menu page %}
    </li>
    {% endif %}
    {% endif %}
    {% endfor %}
    </ul>

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
manager ``mezzanine.core.managers.PublishedManager`` provide common
features for items that can be displayed on the site with their own
URLs (also known as slugs). Mezzanine's ``Page`` model subclasses it.
Some of its features are:

  * Meta data such as a title, description and keywords.
  * Auto-generated slug from the title.
  * Draft/published status with the ability to preview drafts.
  * Pre-dated publishing.
  * Searchable by Mezzanine's :doc:`search-engine`.

Models that do not inherit from the ``Page`` model described earlier
should subclass the ``Displayable`` model if any of the above features
are required. An example of this can be found in the ``mezzanine.blog``
application, where ``BlogPost`` instances contain their own URLs and
views that fall outside of the regular URL/view structure of the
``Page`` model.

Third-party App Integration
---------------------------

A common requirement when using regular Django apps with Mezzanine is
for pages in the site's navigation to point to the urlpatterns for the
app. Implementing this simply requires creating a page with a URL used
by the application. The template rendered by the application's view
will have a ``page`` variable in its context, that contains the current
page object that was created with the same URL.
