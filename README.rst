Overview
--------

Mezzanine is a content management platform built using the `Django`_ framework. It is BSD licenced and designed to provide both a consistant interface for managing content, and a simple archtiecture that makes diving in and hacking on the code as easy as possible.

Its goal is to resemble something like `Wordpress`_, with an intuitive interface for managing pages and blog posts. Mezzanine takes a different approach from a lot of other Django applications in this space like `Pinax`_ or `Mingus`_ that glue together a lot of reusable apps, instead opting to provide most of its functionality included with the project by default.

Dependencies
------------

Apart from `Django`_ itself, Mezzanine has no explicit dependencies but is designed to be used most effectively in conjunction with the following libraries.

  * `setuptools`_
  * `Python Imaging Library`_ (PIL)
  * `django-grappelli`_ <= 2.0
  * `django-filebrowser`_

Installation
------------

Assuming you have `setuptools`_ installed, the easiest method is to install directly from Pypi by running the following command, which will also attempt to install the dependencies mentioned above::

    $ easy_install -U mezzanine

Otherwise you can download Mezzanine and install it directly from source::

    $ python setup.py install
    
Once installed the command ``mezzanine-project`` should be available which can be for creating a new Mezzaine project in a similar fashion to ``django-admin.py``::

    $ mezzanine-project project_name

Features
--------

On top of all the usual features provided by Django such as MVC architecture, ORM, templating, caching and the automatic admin interface, Mezzanine provides the following features.

  * Hierarchical page navigation
  * Save as draft and preview on site
  * Drag-n-drop page ordering
  * WYSIWYG editing
  * SEO friendly URLs and meta data
  * Mobile device detection and templates
  * Blogging engine
  * Tagging
  * Built-in threaded comments, or:
  * Disqus integration
  * Gravatar integration
  * Google Analytics integration
  * Twitter feed integration
  * bit.ly integration
  * Sharing via Facebook or Twitter
  * Custom templates per page or blog post

The Mezzanine admin dashboard

.. image:: http://media.tumblr.com/tumblr_l3su7jFBHM1qa0qji.png

Sites Using Mezzanine
---------------------

  * `Citrus Agency`_

.. _`Django`: http://djangoproject.com/
.. _`Wordpress`: http://wordpress.org/
.. _`Pinax`: http://pinaxproject.com/
.. _`Mingus`: http://github.com/montylounge/django-mingus
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`Python Imaging Library`: http://www.pythonware.com/products/pil/
.. _`django-grappelli`: http://code.google.com/p/django-grappelli/
.. _`django-filebrowser`: http://code.google.com/p/django-filebrowser/
.. _`Citrus Agency`: http://citrus.com.au/

