======
Themes
======

Mezzanine leverages the concept of 
`Django reusable apps <http://ericholscher.com/projects/django-conventions/app/>`_ 
to provide a structure for themes that can be used to change the look of 
your Mezzanine project. In its simplest form, a Mezzanine theme provides 
a set of templates and assets such as images, Javascript and CSS files. 
Using the concept of Django reusable apps, a theme can be also be quite 
advanced providing its own data models, forms and views.

.. note:: 

    If you're well versed in how to work with Django applications in your 
    project then you can skip this section - there are no special 
    considerations to make for a Mezzanine theme and your normal work-flow 
    of adding an installed application to your project and overriding its 
    templates is entirely applicable.

Installing Themes
=================

As mentioned, a Mezzanine theme is synonymous with a Django reusable 
app. This means that the process of adding it to your project involves 
`installing the theme as a Python package <http://docs.python.org/install/index.html#standard-build-and-install>`_ 
and then adding it to your project's ``INSTALLED_APPS`` setting. 

In order to facilitate adding a theme's templates and assets into your 
project so that they can be easily customised and hosted, Mezzanine 
provides a `Django management command <http://docs.djangoproject.com/en/dev/ref/django-admin/>`_ 
``install_theme`` that will copy all of the templates for the theme into 
your project's ``templates`` directory where you can then edit the templates 
without modifying the theme itself. For example suppose you had a theme 
called ``mytheme`` that you've added as a regular Python package, in your 
project's directory you would run the following command::

    $ python manage.py install_theme mytheme

The ``install_theme`` command will also copy any assets such as images, 
Javascript and CSS files into the directory specified by the ``MEDIA_ROOT`` 
setting in your project's ``settings`` module (``site_media`` by default).

If a theme simply provides templates and other asset files, by running the 
``install_theme`` command you shouldn't need to add the theme to your 
``INSTALLED_APPS`` setting as you normally would for a Django reusable app.

Creating Themes
===============

Mezzanine provides features for setting up the required files for a theme 
as well as injecting the theme's files into your project during its
development. 

Setting up a new theme is provided via a Django management 
command ``start_theme``. This command leverages Django's ``startapp`` 
command and creates a directory for your new theme. It also copies all of 
the templates and assets from your project, essentially allowing you to 
take a snapshot of your project and turn it into a standalone theme at any 
time. For example to create a new theme called ``mytheme``, in your 
project's directory you would run the following command::

    $ python manage.py start_theme mytheme

This will create the ``mytheme`` application directory inside your project 
along with the standard modules a Django application uses. It will also 
contains a ``templates`` and a ``media`` directory for templates and other 
assets respectively, as required by a Mezzanine template.

In order to develop your theme in its own directory, you can set the value 
of the ``THEME`` setting in your project's ``settings`` module to the name 
of your theme. This will ensure that its templates and asset files are used 
when running your project locally during development. As usual you should 
add the theme to your ``INSTALLED_APPS`` setting in order to develop 
regular Django features for your theme such as models or custom template tags.

When creating a theme the following points should be considered:

  * Include a README file documenting any useful information for your users.
  * If your theme includes extra functionality, add tests in your theme's ``test.py`` module.
  * Package your theme on `pypi <http://docs.python.org/distutils/introduction.html#simple-example>`_ - this allows your theme to be installed in as little as two commands.
  * Be mindful of the ``editable`` template tags - these provide in-line editing capabilities. If you add your own modules to your theme, be sure to make them `in-line editable <inline-editing.html>`_.
  * Be sure to ``include`` the ``includes/footer_scripts.html`` template at the end of your base template. This provides features such as Google Analytics and most importantly in-line editing of content.

