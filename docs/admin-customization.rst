===================
Admin Customization
===================

Mezzanine uses the standard `Django admin interface
<http://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_ allowing you to
add admin classes as you normally would with a Django project, but also
provides the following enhancements to the admin interface that are
configurable by the developer.

Navigation
==========

When first logging into the standard Django admin interface a user is
presented with the list of models that they have permission to modify data
for. Mezzanine takes this feature and uses it to provide a navigation menu
that persists across every section of the admin interface making the list
of models always accessible.

Using the standard Django admin the grouping and ordering of these models
aren't configurable, so Mezzanine provides the setting
``ADMIN_MENU_ORDER`` that can be used to control the grouping and
ordering of models when listed in the admin area.

This setting is a sequence of pairs where each pair represents a group of
models. The first item in each pair is the name to give the group and the
second item is the sequence of app/model names to use for the group. The
ordering of both the groups and their models is maintained when they are
displayed in the admin area.

For example, to specify two groups ``Content`` and ``Site`` in your admin
with the first group containing models from Mezzanine's ``pages`` and
``blog`` apps, and the second with the remaining models provided by Django,
you would define the following in your projects's ``settings`` module::

    ADMIN_MENU_ORDER = (
        ("Content", ("pages.Page", "blog.BlogPost", "blog.Comment",)),
        ("Site", ("auth.User", "auth.Group", "sites.Site", "redirects.Redirect")),
    )

Any admin classes that aren't specifed are included using Django's normal
approach of grouping models alphabetically by application name. You can
also control this behavior by implementing a ``in_menu`` method on your
admin class, which should return ``True`` or ``False``. When implemented,
this method controls whether the admin class appears in the menu or not.
Here's an advanced example that excludes the ``BlogCategoryAdmin`` class
from the menu, unless it is explicitly defined in ``ADMIN_MENU_ORDER``::

    from django.contrib import admin

    class BlogCategoryAdmin(admin.ModelAdmin):
        """
        Admin class for blog categories. Hides itself from the admin menu
        unless explicitly specified.
        """

        fieldsets = ((None, {"fields": ("title",)}),)

        def in_menu(self):
            """
            Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
            """
            for (name, items) in settings.ADMIN_MENU_ORDER:
                if "blog.BlogCategory" in items:
                    return True
            return False


Custom Items
============

It is possible to inject custom navigation items into the
``ADMIN_MENU_ORDER`` setting by specifying an
item using a two item sequence, the first item containing the title and
second containing the named urlpattern that resolves to the url to be used.

Continuing on from the previous example, Mezzanine includes a fork of the
popular `django-filebrowser <http://code.google.com/p/django-filebrowser/>`_
application which contains a named urlpattern ``fb_browse`` and is given
the title ``Media Library`` to create a custom navigation item::

    ADMIN_MENU_ORDER = (
        ("Content", ("pages.Page", "blog.BlogPost", "blog.Comment",
            ("Media Library", "fb_browse"),)),
        ("Site", ("auth.User", "auth.Group", "sites.Site", "redirects.Redirect")),
    )

You can also use this two-item sequence approach for regular app/model
names if you'd like to give them a custom title.

Dashboard
=========

When using the standard Django admin interface, the dashboard area shown
when a user first logs in provides the list of available models and a list
of the user's recent actions. Mezzanine makes this dashboard configurable
by the developer by providing a system for specifying Django `Inclusion Tags
<http://docs.djangoproject.com/en/dev/howto/custom-template-tags/#inclusion-tags>`_
that will be displayed in the dashboard area.

The dashboard area is broken up into three columns, the first being wide and
the second and third being narrow. Mezzanine then provides the setting
``DASHBOARD_TAGS`` which is a sequence of three sequences - one for
each the three columns. Each sequence contains the names of the inclusion
tags in the format ``tag_lib.tag_name`` that will be rendered in each of the
columns .

The list of models and recent actions normally found in the Django admin are
available as inclusion tags via ``mezzanine_tags.app_list`` and
``mezzanine_tags.recent_actions`` respectively. For example, to configure the
dashboard with a blog form above the model list in
the first column, a list of recent comments in the second column and the
recent actions list in the third column, you would define the following in
your projects's ``settings`` module::

    DASHBOARD_TAGS = (
        ("blog_tags.quick_blog", "mezzanine_tags.app_list"),
        ("comment_tags.recent_comments",),
        ("mezzanine_tags.recent_actions",),
    )

Here we can see the ``quick_blog`` inclusion tag provided by the
``mezzanine.blog.templatetags.blog_tags`` module and the
``recent_comments`` inclusion tag provided by the
``mezzanine.generic.templatetags.comment_tags`` module.

WYSIWYG Editor
==============

By default, Mezzanine uses the
`TinyMCE editor <http://tinymce.moxiecode.com/>`_ to provide rich
editing for all model fields of the type
``mezzanine.core.fields.RichTextField``. The setting ``RICHTEXT_WIDGET_CLASS``
contains the import path to the widget class that will be used for
editing each of these fields, which therefore provides the ability for
implementing your own editor widget which could be a modified version
of TinyMCE, a different editor or even no editor at all.

.. note::

    If you'd only like to customize the TinyMCE options specified in its
    JavaScript setup, you can do so via the ``TINYMCE_SETUP_JS`` setting
    which lets you specify the URL to your own TinyMCE setup JavaScript
    file.

The default value for the ``RICHTEXT_WIDGET_CLASS`` setting is the
string ``"mezzanine.core.forms.TinyMceWidget"``. The ``TinyMceWidget``
class referenced here provides the necessary media files and HTML for
implementing the TinyMCE editor, and serves as a good reference point
for implementing your own widget class which would then be specified
via the ``RICHTEXT_WIDGET_CLASS`` setting.

In addition to ``RICHTEXT_WIDGET_CLASS`` you may need to customize the
way your content is rendered at the template level. Post processing of
the content can be achieved through the ``RICHTEXT_FILTERS`` setting,
which is a sequence of string, each one containing the dotted path to
a Python function, that will be used as a processing pipeline for the
content. Think of them like Django's middleware or context processors.

Say, for example, you had a ``RICHTEXT_WIDGET_CLASS`` that allowed you
to write your content in a popular wiki syntax such as markdown. You'd
need a way to convert that wiki syntax into HTML right before the
content was rendered::

    # ... in myproj.filter
    from markdown import markdown

    def markdown_filter(content):
        """
        Converts markdown formatted content to html
        """
        return markdown(content)

    # ... in myproj.settings
    RICHTEXT_FILTERS = (
        "myproj.filter.markdown_filter",
    )

With the above, you'd now see the converted HTML content rendered to
the template, rather than the raw markdown formatting.

Media Library Integration
=========================

Mezzanine's Media Library (based on django-filebrowser) provides a
`jQuery UI <http://jqueryui.com/>`_ `dialog <http://jqueryui.com/dialog/>`_ that can be used by custom widgets to allow users to select previously
uploaded files.

When using a custom widget for the WYSIWYG editor via the
``RICHTEXT_WIDGET_CLASS`` setting, you can show the Media Library dialog
from your custom widget, by doing the following:

1. Load the following media resources in your widget, perhaps using a
   `Django Media inner class
   <https://docs.djangoproject.com/en/dev/topics/forms/media/>`_:

   :css:
      ``filebrowser/css/smoothness/jquery-ui-1.9.1.custom.min.css``
   :js:
      | ``mezzanine/js/%s' % settings.JQUERY_FILENAME``
      | ``filebrowser/js/jquery-ui-1.9.1.custom.min.js``
      | ``filebrowser/js/filebrowser-popup.js``

2. Call the JavaScript function ``browseMediaLibrary`` to show the
   dialog. The function is defined in
   ``filebrowser/js/filebrowser-popup.js``, and takes the following
   two arguments:

   :Callback function:
      The function that will be called after the dialog is closed. The
      function will be called with a single argument, which will be:

      - null: if no selection was made (e.g. dialog is closed by
        hitting `ESC`), or
      - the path of the selected file.

   :Type (optional): Type of files that are selectable in the
      dialog. Defaults to image.

Singleton Admin
===============

The admin class ``mezzanine.core.admin.SingletonAdmin`` is a utility
that can be used to create an admin interface for managing the case
where only a single instance of a model should exist. Some cases
include a single page site, where only a few fixed blocks of text
need to be maintained. Perhaps a stand-alone admin section is
required for managing a site-wide alert. There's overlap here with
Mezzanine's :doc:`configuration` admin interface, but you may have a
case that warrants its own admin section. Let's look at an example of
a site-wide alert model, that should only ever have a single record
in the database.

Here's a model with a text field for managing the alert::

    from django.db import models

    class SiteAlert(models.Model):

        message = models.TextField(blank=True)

        # Make the plural name singular, to correctly
        # label it in the admin interface.
        class Meta:
            verbose_name_plural = "Site Alert"

Here's our ``admin.py`` module in the same app::

    from mezzanine.core.admin import SingletonAdmin
    from .models import SiteAlert

    # Subclassing allows us to customize the admin class,
    # but you could also register your model directly
    # against SingletonAdmin below.
    class SiteAlertAdmin(SingletonAdmin):
        pass

    admin.site.register(SiteAlert, SiteAlertAdmin)

What we achieve by using ``SingletonAdmin`` above, is an admin
interface that hides the usual listing interface that lists all
records in the model's database table. When going to the "Site Alert"
section of the admin, the user will be taken directly to the editing
interface.
