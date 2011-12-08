========
Overview
========

Mezzanine is a content management platform built using the `Django`_
framework. It is `BSD licensed`_ and designed to provide both a consistent
interface for managing content, and a simple architecture that makes diving
in and hacking on the code as easy as possible.

Mezzanine resembles tools like `Wordpress`_, with an intuitive
interface for managing pages and blog posts. Mezzanine takes a different
approach from other Django applications in this space like `Pinax`_ or
`Mingus`_ that glue together a lot of reusable apps, instead opting to
provide most of its functionality included with the project by default.

Visit the `gallery of sites powered by Mezzanine`_ to see some of the
great sites people have built using Mezzanine.

Features
========

On top of all the usual features provided by Django such as MVC architecture,
ORM, templating, caching and the automatic admin interface, Mezzanine
provides the following features:

  * Hierarchical page navigation
  * Save as draft and preview on site
  * Scheduled publishing
  * Drag-n-drop page ordering
  * WYSIWYG editing
  * `In-line page editing`_
  * Drag-n-drop HTML5 forms builder with CSV export
  * API for `custom content types`_
  * SEO friendly URLs and meta data
  * `Search engine and API`_
  * Configurable `dashboard`_ widgets
  * Multi-device detection and template handling
  * Shopping cart module (`Cartridge`_)
  * Blogging engine
  * `Themes`_
  * Tagging
  * One step migration from other blogging engines
  * `Disqus`_ integration or built-in threaded comments
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
environment using:

  * `Python`_ 2.5 ... 2.7
  * `Django`_ 1.1 ... 1.3

Mezzanine is designed however to be used most effectively in conjunction
with the following libraries:

  * `Python Imaging Library`_ (PIL)
  * `django-grappelli`_ <= 2.0
  * `django-filebrowser`_ <= 3.0
  * `South`_
  * `pyflakes`_ and `pep8`_ (required for running the test suite)

Browser Support
===============

Mezzanine's admin interface works with all modern browsers.
Internet Explorer 7 and earlier are generally unsupported.

Installation
============

The easiest method is to install directly from pypi using `pip`_ or
`setuptools`_ by running the respective command below, which will also
attempt to install the dependencies mentioned above::

    $ pip install -U mezzanine

or::

    $ easy_install -U mezzanine

Otherwise you can download Mezzanine and install it directly from source::

    $ python setup.py install

Once installed, the command ``mezzanine-project`` should be available which
can be used for creating a new Mezzanine project in a similar fashion to
``django-admin.py``::

    $ mezzanine-project project_name

You can then run your project with the usual Django steps::

    $ cd project_name
    $ python manage.py createdb --noinput
    $ python manage.py runserver

.. note::

    The ``createdb`` command performs the same task as Django's ``syncdb``
    command, and also handles setting the initial migration state for `South`_.

You should then be able to browse to http://127.0.0.1:8000/admin/ and log
in using the default account (``username: admin, password: default``). If
you'd like to specify a different username and password during set up, simply
exclude the ``--noinput`` option included above when running ``createdb``.

Contributing
============

Mezzanine is an open source project that is managed using both Git and
Mercurial version control systems. These repositories are hosted on both
`Github`_ and `Bitbucket`_ respectively, so contributing is as easy as
forking the project on either of these sites and committing back your
enhancements.

Please note the following points around contributing:

  * Contributed code must be written in the existing style. This is as simple as following the `Django coding style`_ and most importantly `PEP 8`_.
  * Contributions must be available on a separately named branch that is based on the latest version of the main branch.
  * Run the tests before committing your changes. If your changes causes the tests to break, they won't be accepted.
  * If you're adding new functionality, you must include basic tests and documentation.

Third-party Modules
===================

The following modules have been developed outside of Mezzanine. If you
have developed a module to integrate with Mezzanine and would like it
listed here, send an email to the `mezzanine-users`_ mailing list.

  * `mezzanine-html5boilerplate`_ - Integrates the `html5boilerplate project`_ into Mezzanine.
  * `mezzanine-mdown`_ - Adds `Markdown`_ support to Mezzanine's rich text editor.
  * `mezzanine-openshift`_ Setup for running Mezzanine on `Redhat's OpenShift` cloud platform.

Donating
========

If you would like to make a donation to continue development of the
project, you can do so via the `Mezzanine Project`_ website.

Support
=======

For general questions or comments, please join the
`mezzanine-users`_ mailing list. To report a bug or other type of issue,
please use the `Github issue tracker`_.

Sites Using Mezzanine
=====================

  * `Citrus Agency`_
  * `Mezzanine Project`_
  * `Nick Hagianis`_
  * `Thomas Johnson`_
  * `Central Mosque Wembley`_
  * `Ovarian Cancer Research Foundation`_
  * `The Source Procurement`_
  * `Imageinary`_
  * `Brad Montgomery`_
  * `Jashua Cloutier`_
  * `Alpha & Omega Contractors`_
  * `Equity Advance`_
  * `Head3 Interactive`_
  * `PyLadies`_
  * `Ripe Maternity`_
  * `Cotton On`_
  * `List G Barristers`_
  * `Tri-Cities Flower Farm`_
  * `daon.ru`_
  * `autoindeks.ru`_
  * `immiau.ru`_
  * `ARA Consultants`_
  * `Boîte à Z'images`_
  * `The Melbourne Cup`_
  * `Diablo News`_
  * `Goldman Travel`_

Quotes
======

  * "I am enjoying working with Mezzanine - it is good work." - `Van Lindberg`_
  * "Mezzanine looks pretty interesting - tempting to get me off Wordpress." - `Jesse Noller`_
  * "Mezzanine is amazing." - `Audrey Roy`_
  * "Mezzanine convinced me to switch from the Ruby world over to Python." - `Michael Delaney`_
  * "Impressed with Mezzanine so far." - `Brad Montgomery`_
  * "From the moment I installed Mezzanine, I have been delighted, both with the initial experience and the community involved in its development." - `John Campbell`_
  * "You need to check out the open source project Mezzanine. In one word: Elegant." - `Nick Hagianis`_
  * "Who came up with the name Mezzanine? I love it, like a platform between the client's ideas and their published website. Very classy!" - `Stephen White`_

.. _`Django`: http://djangoproject.com/
.. _`BSD licensed`: http://www.linfo.org/bsdlicense.html
.. _`Wordpress`: http://wordpress.org/
.. _`Pinax`: http://pinaxproject.com/
.. _`Mingus`: http://github.com/montylounge/django-mingus
.. _`gallery of sites powered by Mezzanine`: http://mezzanine.jupo.org/sites/
.. _`Python`: http://python.org/
.. _`pip`: http://www.pip-installer.org/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`Python Imaging Library`: http://www.pythonware.com/products/pil/
.. _`django-grappelli`: http://code.google.com/p/django-grappelli/
.. _`django-filebrowser`: http://code.google.com/p/django-filebrowser/
.. _`South`: http://south.aeracode.org/
.. _`pyflakes`: http://pypi.python.org/pypi/pyflakes
.. _`pep8`: http://pypi.python.org/pypi/pep8
.. _`In-line page editing`: http://mezzanine.jupo.org/docs/inline-editing.html
.. _`custom content types`: http://mezzanine.jupo.org/docs/content-architecture.html#creating-custom-content-types
.. _`Search engine and API`: http://mezzanine.jupo.org/docs/search-engine.html
.. _`dashboard`: http://mezzanine.jupo.org/docs/admin-customization.html#dashboard
.. _`Cartridge`: http://cartridge.jupo.org/
.. _`Themes`: http://mezzanine.jupo.org/docs/themes.html
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
.. _`mezzanine-users`: http://groups.google.com/group/mezzanine-users/topics
.. _`Github issue tracker`: http://github.com/stephenmcd/mezzanine/issues
.. _`Citrus Agency`: http://citrus.com.au/
.. _`Mezzanine Project`: http://mezzanine.jupo.org/
.. _`Nick Hagianis`: http://hagianis.com/
.. _`Thomas Johnson`: http://tomfmason.net/
.. _`Central Mosque Wembley`: http://wembley-mosque.co.uk/
.. _`Ovarian Cancer Research Foundation`: http://ocrf.com.au/
.. _`The Source Procurement`: http://thesource.com.au/
.. _`Imageinary`: http://imageinary.com/
.. _`Van Lindberg`: http://www.lindbergd.info/
.. _`Jesse Noller`: http://jessenoller.com/
.. _`Audrey Roy`: http://cartwheelweb.com/
.. _`John Campbell`: http://head3.com/
.. _`Stephen White`: http://bitbucket.org/swhite/
.. _`Michael Delaney`: http://github.com/fusepilot/
.. _`Brad Montgomery`: http://blog.bradmontgomery.net/
.. _`Jashua Cloutier`: http://www.senexcanis.com/
.. _`Alpha & Omega Contractors`: http://alphaomegacontractors.com/
.. _`Equity Advance`: http://equityadvance.com.au/
.. _`Head3 Interactive`: http://head3.com/
.. _`PyLadies`: http://www.pyladies.com/
.. _`Ripe Maternity`: http://www.ripematernity.com/
.. _`Cotton On`: http://shop.cottonon.com/
.. _`List G Barristers`: http://www.listgbarristers.com.au/
.. _`Tri-Cities Flower Farm`: http://www.tricitiesflowerfarm.com/
.. _`daon.ru`: http://daon.ru/
.. _`autoindeks.ru`: http://autoindeks.ru/
.. _`immiau.ru`: http://immiau.ru/
.. _`ARA Consultants`: http://www.araconsultants.com.au/
.. _`Boîte à Z'images`: http://boiteazimages.com/
.. _`The Melbourne Cup`: http://www.melbournecup.com/
.. _`Diablo News`: http://www.diablo-news.com/
.. _`Django coding style`: http://docs.djangoproject.com/en/dev/internals/contributing/#coding-style
.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/
.. _`mezzanine-html5boilerplate`: https://github.com/tvon/mezzanine-html5boilerplate
.. _`html5boilerplate project`: http://html5boilerplate.com/
.. _`mezzanine-mdown`: https://bitbucket.org/onelson/mezzanine-mdown
.. _`Markdown`: http://en.wikipedia.org/wiki/Markdown
.. _`mezzanine-openshift`: https://github.com/k4ml/mezzanine-openshift
.. _`Redhat's OpenShift`: https://openshift.redhat.com/
.. _`Goldman Travel`: http://www.goldmantravel.com.au/
