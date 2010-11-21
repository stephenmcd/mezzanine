========
Overview
========

Mezzanine is a content management platform built using the `Django`_ 
framework. It is `BSD licensed`_ and designed to provide both a consistent 
interface for managing content, and a simple architecture that makes diving 
in and hacking on the code as easy as possible.

Its goal is to resemble something like `Wordpress`_, with an intuitive 
interface for managing pages and blog posts. Mezzanine takes a different 
approach from other Django applications in this space like `Pinax`_ or 
`Mingus`_ that glue together a lot of reusable apps, instead opting to 
provide most of its functionality included with the project by default.

Features
========

On top of all the usual features provided by Django such as MVC architecture, 
ORM, templating, caching and the automatic admin interface, Mezzanine 
provides the following features.

  * Hierarchical page navigation
  * Save as draft and preview on site
  * Scheduled publishing
  * Drag-n-drop page ordering
  * WYSIWYG editing
  * `In-line page editing`_
  * Drag-n-drop forms builder with CSV export
  * API for `custom content types`_
  * SEO friendly URLs and meta data
  * `Search engine and API`_
  * Configurable `dashboard`_ widgets
  * Mobile device detection and templates
  * Shopping cart module (`Cartridge`_)
  * Blogging engine
  * Tagging
  * One step migration from other blogging engines
  * Built-in threaded comments, or:
  * `Disqus`_ integration
  * `Gravatar`_ integration
  * `Google Analytics`_ integration
  * `Twitter`_ feed integration
  * `bit.ly`_ integration
  * Sharing via Facebook or Twitter
  * `Custom templates`_ per page or blog post
  * Built-in `test suite`_
  * `960.gs`_ integration

The Mezzanine admin dashboard:

.. image:: http://github.com/stephenmcd/mezzanine/raw/master/docs/img/dashboard.png

Dependencies
============

Mezzanine has no explicit dependencies apart from a standard Django 
environment using.

  * `Python`_ 2.5 ... 2.7
  * `Django`_ 1.1 ... 1.3
  
Mezzanine is designed however to be used most effectively in conjunction 
with the following libraries.

  * `setuptools`_
  * `Python Imaging Library`_ (PIL)
  * `django-grappelli`_ <= 2.0
  * `django-filebrowser`_ <= 3.0

Installation
============

Assuming you have `setuptools`_ installed, the easiest method is to install 
directly from pypi by running the following command, which will also attempt 
to install the dependencies mentioned above::

    $ easy_install -U mezzanine

Otherwise you can download Mezzanine and install it directly from source::

    $ python setup.py install
    
Once installed, the command ``mezzanine-project`` should be available which 
can be used for creating a new Mezzanine project in a similar fashion to 
``django-admin.py``::

    $ mezzanine-project project_name

You can then run your project with the usual Django steps::

    $ cd project_name
    $ python manage.py syncdb --noinput
    $ python manage.py runserver
    
You should then be able to browse to http://127.0.0.1:8000/admin/ and log 
in using the default account (``username: admin, password: default``). If 
you'd like to specify a different username and password during set up, simply 
exclude the ``--noinput`` option included above when running ``syncdb``.

Contributing
============

Mezzanine is an open source project that is managed using both Git and 
Mercurial version control systems. These repositories are hosted on both 
`Github`_ and `Bitbucket`_ respectively, so contributing is as easy as 
forking the project on either of these sites and committing back your 
enhancements. 

Support
=======

For general questions or comments, please join the 
`mezzanine-users`_ mailing list. To report a bug or other type of issue, 
please use the `Github issue tracker`_.

Sites Using Mezzanine
=====================

  * `Citrus Agency`_
  * `Mezzanine Project`_ (self hosted)
  * `Nick Hagianis`_
  * `Thomas Johnson`_
  * `Central Mosque Wembley`_
  * `Ovarian Cancer Research Foundation`_

Quotes
======

  * "I am enjoying working with Mezzanine - it is good work." - `Van Lindberg`_
  * "Impressed with Mezzanine so far." - `Brad Montgomery`_
  * "You need to check out the open source project Mezzanine. In one word: Elegant." - `Nick Hagianis`_
  * "Mezzanine looks pretty interesting - tempting to get me off Wordpress." - `Jesse Noller`_
  * "Who came up with the name Mezzanine? I love it, like a platform between the client's ideas and their published website. Very classy!" - `Stephen White`_

.. _`Django`: http://djangoproject.com/
.. _`BSD licensed`: http://www.linfo.org/bsdlicense.html
.. _`Wordpress`: http://wordpress.org/
.. _`Pinax`: http://pinaxproject.com/
.. _`Mingus`: http://github.com/montylounge/django-mingus
.. _`Python`: http://python.org/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`Python Imaging Library`: http://www.pythonware.com/products/pil/
.. _`django-grappelli`: http://code.google.com/p/django-grappelli/
.. _`django-filebrowser`: http://code.google.com/p/django-filebrowser/
.. _`In-line page editing`: http://mezzanine.jupo.org/docs/inline-editing.html
.. _`custom content types`: http://mezzanine.jupo.org/docs/content-architecture.html#creating-custom-content-types
.. _`Search engine and API`: http://mezzanine.jupo.org/docs/search-engine.html
.. _`dashboard`: http://mezzanine.jupo.org/docs/admin-customization.html#dashboard
.. _`Cartridge`: http://cartridge.jupo.org/
.. _`Custom templates`: http://mezzanine.jupo.org/docs/content-architecture.html#page-templates
.. _`test suite`: http://mezzanine.jupo.org/docs/packages.html#module-mezzanine.tests
.. _`960.gs`: http://960.gs/
.. _`Disqus`: http://disqus.com/
.. _`Gravatar`: http://gravatar.com/
.. _`Google Analytics`: http://www.google.com/analytics/
.. _`Twitter`: http://twitter.com/
.. _`bit.ly`: http://bit.ly/
.. _`Github`: http://github.com/stephenmcd/mezzanine/
.. _`Bitbucket`: http://bitbucket.org/stephenmcd/mezzanine/
.. _`mezzanine-users`: http://groups.google.com/group/mezzanine-users
.. _`Github issue tracker`: http://github.com/stephenmcd/mezzanine/issues
.. _`Citrus Agency`: http://citrus.com.au/
.. _`Mezzanine Project`: http://mezzanine.jupo.org/
.. _`Nick Hagianis`: http://hagianis.com/
.. _`Thomas Johnson`: http://tomfmason.net/
.. _`Central Mosque Wembley`: http://wembley-mosque.co.uk/
.. _`Ovarian Cancer Research Foundation`: http://ocrf.com.au/
.. _`Van Lindberg`: http://www.lindbergd.info/
.. _`Jesse Noller`: http://jessenoller.com/
.. _`Stephen White`: http://bitbucket.org/swhite/
.. _`Brad Montgomery`: http://bradmontgomery.net/
