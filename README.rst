
  .. image:: https://secure.travis-ci.org/stephenmcd/mezzanine.png?branch=master

Created by `Stephen McDonald <http://twitter.com/stephen_mcd>`_

========
Overview
========

Mezzanine is a powerful, consistent, and flexible content management
platform. Built using the `Django`_ framework, Mezzanine provides a
simple yet highly extensible architecture that encourages diving in
and hacking on the code. Mezzanine is `BSD licensed`_ and supported by
a diverse and active community.

In some ways, Mezzanine resembles tools such as `Wordpress`_ that
provide an intuitive interface for managing pages, blog posts, form
data, store products, and other types of content. But Mezzanine is
also different. Unlike many other platforms that make extensive use of
modules or reusable applications, Mezzanine provides most of its
functionality by default. This approach yields a more integrated and
efficient platform.

Visit the `Mezzanine project page`_ to see some of the `great sites
people have built using Mezzanine`_.

Features
========

In addition to the usual features provided by Django such as MVC
architecture, ORM, templating, caching and an automatic admin
interface, Mezzanine provides the following:

  * Hierarchical page navigation
  * Save as draft and preview on site
  * Scheduled publishing
  * Drag-and-drop page ordering
  * WYSIWYG editing
  * `In-line page editing`_
  * Drag-and-drop HTML5 forms builder with CSV export
  * SEO friendly URLs and meta data
  * Shopping cart module (`Cartridge`_)
  * Configurable `dashboard`_ widgets
  * Blog engine
  * Tagging
  * User accounts and profiles with email verification
  * Translated to over 20 languages
  * Sharing via Facebook or Twitter
  * `Custom templates`_ per page or blog post
  * `Twitter Bootstrap`_ integration
  * API for `custom content types`_
  * `Search engine and API`_
  * Seamless integration with third-party Django apps
  * Multi-device detection and template handling
  * One step migration from other blogging engines
  * Automated production provisioning and deployments
  * `Disqus`_ integration, or built-in threaded comments
  * `Gravatar`_ integration
  * `Google Analytics`_ integration
  * `Twitter`_ feed integration
  * `bit.ly`_ integration
  * `Akismet`_ spam filtering
  * Built-in `test suite`_

The Mezzanine admin dashboard:

.. image:: http://github.com/stephenmcd/mezzanine/raw/master/docs/img/dashboard.png

Dependencies
============

Mezzanine makes use of as few libraries as possible (apart from a
standard Django environment), with the following dependencies:

  * `Python`_ 2.5 ... 2.7
  * `Django`_ 1.3 ... 1.4
  * `Python Imaging Library`_ - for image resizing
  * `grappelli-safe`_ - admin skin (`Grappelli`_ fork)
  * `filebrowser-safe`_ - for managing file uploads (`FileBrowser`_ fork)
  * `bleach`_ - for sanitizing markup in content
  * `pytz`_ - for timezone support
  * `South`_ - for database migrations (optional)
  * `django-compressor`_ - for merging JS/CSS assets (optional)
  * `pyflakes`_ and `pep8`_ - for running the test suite (optional)

Browser Support
===============

Mezzanine's admin interface works with all modern browsers.
Internet Explorer 7 and earlier are generally unsupported.

Installation
============

The easiest method is to install directly from pypi using `pip`_ by
running the command below, which will also install the required
dependencies mentioned above::

    $ pip install -U mezzanine

If you prefer, you can download Mezzanine and install it directly from
source::

    $ python setup.py install

Once installed, the command ``mezzanine-project`` can be used to
create a new Mezzanine project in similar fashion to
``django-admin.py``::

    $ mezzanine-project project_name
    $ cd project_name
    $ python manage.py createdb --noinput
    $ python manage.py runserver

.. note::

    The ``createdb`` is a shortcut for using Django's ``syncdb``
    command and setting the initial migration state for `South`_. You
    can alternatively use ``syncdb`` and ``migrate`` if preferred.
    South is automatically added to INSTALLED_APPS if the
    ``USE_SOUTH`` setting is set to ``True``.

You should then be able to browse to http://127.0.0.1:8000/admin/ and
log in using the default account (``username: admin, password:
default``). If you'd like to specify a different username and password
during set up, simply exclude the ``--noinput`` option included above
when running ``createdb``.

For information on how to add Mezzanine to an existing Django project,
see the FAQ section of the documentation.

Contributing
============

Mezzanine is an open source project managed using both the Git and
Mercurial version control systems. These repositories are hosted on
both `GitHub`_ and `Bitbucket`_ respectively, so contributing is as
easy as forking the project on either of these sites and committing
back your enhancements.

Please note the following guidelines for contributing:

  * Contributed code must be written in the existing style. This is
    as simple as following the `Django coding style`_ and (most
    importantly) `PEP 8`_.
  * Contributions must be available on a separately named branch
    based on the latest version of the main branch.
  * Run the tests before committing your changes. If your changes
    cause the tests to break, they won't be accepted.
  * If you are adding new functionality, you must include basic tests
    and documentation.

Language Translations
=====================

Mezzanine makes full use of translation strings, which allow Mezzanine
to be translated into multiple languages using `Django's
internationalization`_ methodology. Translations are managed on the
`Transiflex`_ website but can also be submitted via `GitHub`_ or
`Bitbucket`_. Consult the documentation for `Django's
internationalization`_ methodology for more information on creating
translations and using them.

Third-party Modules
===================

The following modules have been developed outside of Mezzanine. If you
have developed a module to integrate with Mezzanine and would like to
list it here, send an email to the `mezzanine-users`_ mailing list.

  * `mezzanine-html5boilerplate`_ - Integrates the
    `html5boilerplate project`_  into Mezzanine.
  * `mezzanine-mdown`_ - Adds `Markdown`_ support to Mezzanine's rich
    text editor.
  * `mezzanine-openshift`_ - Setup for running Mezzanine on
    `Redhat's OpenShift`_ cloud platform.
  * `mezzanine-stackato`_ - Setup for running Mezzanine on
    `ActiveState's Stackato`_ cloud platform.
  * `mezzanine-blocks`_ - A Mezzanine flavored fork of django-flatblocks.
  * `mezzanine-widgets`_ - Widget system for Mezzanine.
  * `mezzanine-themes`_ - A collection of Django/Mezzanine templates.
  * `mezzanine-twittertopic`_ - Manage multiple Twitter topic feeds from
    the Mezzanine admin interface.
  * `mezzanine-captcha`_ - Adds CAPTCHA field types to Mezzanine's forms
    builder app.

Donating
========

If you would like to make a donation to continue development of
Mezzanine, you can do so via the `Mezzanine Project`_ website.

Support
=======

To report a security issue, please send an email privately to
`security@jupo.org`_. This gives us a chance to fix the issue and
create an official release prior to the issue being made
public.

For general questions or comments, please join the `mezzanine-users`_
mailing list. To report a bug or other type of issue, please use the
`GitHub issue tracker`_. And feel free to drop by the `#mezzanine
IRC channel`_ on `Freenode`_, for a chat.

Sites Using Mezzanine
=====================

  * `Citrus Agency <http://citrus.com.au/>`_
  * `Mezzanine Project <http://mezzanine.jupo.org>`_
  * `Nick Hagianis <http://hagianis.com>`_
  * `Thomas Johnson <http://tomfmason.net>`_
  * `Central Mosque Wembley <http://wembley-mosque.co.uk>`_
  * `Ovarian Cancer Research Foundation <http://ocrf.com.au/>`_
  * `The Source Procurement <http://thesource.com.au/>`_
  * `Imageinary <http://imageinary.com>`_
  * `Brad Montgomery <http://blog.bradmontgomery.net>`_
  * `Jashua Cloutier <http://www.senexcanis.com>`_
  * `Alpha & Omega Contractors <http://alphaomegacontractors.com>`_
  * `Equity Advance <http://equityadvance.com.au/>`_
  * `Head3 Interactive <http://head3.com>`_
  * `PyLadies <http://www.pyladies.com>`_
  * `Ripe Maternity <http://www.ripematernity.com/>`_
  * `Cotton On <http://shop.cottonon.com/>`_
  * `List G Barristers <http://www.listgbarristers.com.au>`_
  * `Tri-Cities Flower Farm <http://www.tricitiesflowerfarm.com>`_
  * `daon.ru <http://daon.ru/>`_
  * `autoindeks.ru <http://autoindeks.ru/>`_
  * `immiau.ru <http://immiau.ru/>`_
  * `ARA Consultants <http://www.araconsultants.com.au/>`_
  * `Boîte à Z'images <http://boiteazimages.com/>`_
  * `The Melbourne Cup <http://www.melbournecup.com/>`_
  * `Diablo News <http://www.diablo-news.com>`_
  * `Goldman Travel <http://www.goldmantravel.com.au/>`_
  * `IJC Digital <http://ijcdigital.com/>`_
  * `Coopers <http://store.coopers.com.au/>`_
  * `Joe Julian <http://joejulian.name>`_
  * `Sheer Ethic <http://sheerethic.com/>`_
  * `Salt Lake Magazine <http://saltlakemagazine.com/>`_
  * `Boca Raton Magazine <http://bocamag.com/>`_
  * `Photog.me <http://www.photog.me>`_
  * `Elephant Juice Soup <http://www.elephantjuicesoup.com>`_
  * `National Positions <http://www.nationalpositions.co.uk/>`_
  * `Like Humans Do <http://www.likehumansdo.com>`_
  * `Connecting Countries <http://connectingcountries.net>`_
  * `tindie.com <http://tindie.com>`_
  * `Environmental World Products <http://ewp-sa.com/>`_
  * `Ross A. Laird <http://rosslaird.com>`_
  * `Etienne B. Roesch <http://etienneroes.ch>`_
  * `Recruiterbox <http://recruiterbox.com/>`_
  * `Mod Productions <http://modprods.com/>`_
  * `Appsembler <http://appsembler.com/>`_
  * `Pink Twig <http://www.pinktwig.ca>`_
  * `Parfume Planet <http://parfumeplanet.com>`_
  * `Trading 4 Us <http://www.trading4.us>`_
  * `Chris Fleisch <http://chrisfleisch.com>`_
  * `Theneum <http://theneum.com/>`_
  * `My Story Chest <http://www.mystorychest.com>`_
  * `Philip Sahli <http://www.fatrix.ch>`_
  * `Raymond Chandler <http://www.codearchaeologist.org>`_
  * `Nashsb <http://nashpp.com>`_
  * `AciBASE <http://acinetobacter.bham.ac.uk>`_
  * `Enrico Tröger <http://www.uvena.de>`_
  * `Matthe Wahn <http://www.matthewahn.com>`_
  * `Bit of Pixels <http://bitofpixels.com>`_
  * `Nimbis Services <http://schott.nimbis.net>`_
  * `European Crystallographic Meeting <http://ecm29.ecanews.org>`_
  * `Dreamperium <http://dreamperium.com>`_
  * `UT Dallas <http://utdallasiia.com>`_
  * `Go Yama <http://goyamamusic.com>`_
  * `Yeti LLC <http://www.yetihq.com/>`_
  * `Li Xiong <http://idhoc.com>`_
  * `Pageworthy <http://pageworthy.com>`_
  * `Prince Jets <http://princejets.com>`_
  * `30 sites in 30 days <http://1inday.com>`_
  * `St Barnabas' Theological College <http://www.sbtc.org.au>`_
  * `Helios 3D <http://helios3d.nl/>`_
  * `Life is Good <http://lifeisgoodforall.co.uk/>`_
  * `Brooklyn Navy Yard <http://bldg92.org/>`_
  * `Pie Monster <http://piemonster.me>`_

Quotes
======

  * "I'm enjoying working with Mezzanine, it's good work"
    - `Van Lindberg`_, `Python Software Foundation`_ chairman
  * "Mezzanine looks like it may be Django's killer app"
    - `Antonio Rodriguez`_, ex CTO of `Hewlett Packard`_, founder
    of `Tabblo`_
  * "Mezzanine looks pretty interesting, tempting to get me off
    Wordpress" - `Jesse Noller`_, Python core contributor,
    `Python Software Foundation`_ board member
  * "I think I'm your newest fan. Love these frameworks"
    - `Emile Petrone`_, integrations engineer at `Urban Airship`_
  * "Mezzanine is amazing" - `Audrey Roy`_, founder of `PyLadies`_
    and `Django Packages`_
  * "Mezzanine convinced me to switch from the Ruby world over
    to Python" - `Michael Delaney`_, developer
  * "Like Linux and Python, Mezzanine just feels right" - `Phil Hughes`_,
    Linux For Dummies author, `The Linux Journal`_ columnist
  * "Impressed with Mezzanine so far" - `Brad Montgomery`_, founder
    of `Work For Pie`_
  * "From the moment I installed Mezzanine, I have been delighted, both
    with the initial experience and the community involved in its
    development" - `John Campbell`_, founder of `Head3 Interactive`_
  * "You need to check out the open source project Mezzanine. In one
    word: Elegant" - `Nick Hagianis`_, developer

.. GENERAL LINKS

.. _`Django`: http://djangoproject.com/
.. _`BSD licensed`: http://www.linfo.org/bsdlicense.html
.. _`Wordpress`: http://wordpress.org/
.. _`great sites people have built using Mezzanine`: http://mezzanine.jupo.org/sites/
.. _`Pinax`: http://pinaxproject.com/
.. _`Mingus`: http://github.com/montylounge/django-mingus
.. _`Mezzanine project page`: http://mezzanine.jupo.org
.. _`Python`: http://python.org/
.. _`pip`: http://www.pip-installer.org/
.. _`bleach`: http://pypi.python.org/pypi/bleach
.. _`pytz`: http://pypi.python.org/pypi/pytz/
.. _`django-compressor`: http://pypi.python.org/pypi/django-compressor/
.. _`Python Imaging Library`: http://www.pythonware.com/products/pil/
.. _`grappelli-safe`: http://github.com/stephenmcd/grappelli-safe
.. _`filebrowser-safe`: http://github.com/stephenmcd/filebrowser-safe/
.. _`Grappelli`: http://code.google.com/p/django-grappelli/
.. _`FileBrowser`: http://code.google.com/p/django-filebrowser/
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
.. _`test suite`: http://mezzanine.jupo.org/docs/packages.html#module-mezzanine.core.tests
.. _`Twitter Bootstrap`: http://twitter.github.com/bootstrap/
.. _`Disqus`: http://disqus.com/
.. _`Gravatar`: http://gravatar.com/
.. _`Google Analytics`: http://www.google.com/analytics/
.. _`Twitter`: http://twitter.com/
.. _`bit.ly`: http://bit.ly/
.. _`Akismet`: http://akismet.com/
.. _`project_template`: https://github.com/stephenmcd/mezzanine/tree/master/mezzanine/project_template
.. _`GitHub`: http://github.com/stephenmcd/mezzanine/
.. _`Bitbucket`: http://bitbucket.org/stephenmcd/mezzanine/
.. _`mezzanine-users`: http://groups.google.com/group/mezzanine-users/topics
.. _`security@jupo.org`: mailto:security@jupo.org?subject=Mezzanine+Security+Issue
.. _`GitHub issue tracker`: http://github.com/stephenmcd/mezzanine/issues
.. _`#mezzanine IRC channel`: irc://freenode.net/mezzanine
.. _`Freenode`: http://freenode.net
.. _`Django coding style`: http://docs.djangoproject.com/en/dev/internals/contributing/#coding-style
.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/
.. _`Transiflex`: https://www.transifex.net/projects/p/mezzanine/
.. _`Django's internationalization`: https://docs.djangoproject.com/en/dev/topics/i18n/translation/
.. _`Python Software Foundation`: http://www.python.org/psf/
.. _`Urban Airship`: http://urbanairship.com/
.. _`Django Packages`: http://djangopackages.com/
.. _`Hewlett Packard`: http://www.hp.com/
.. _`Tabblo`: http://www.tabblo.com/
.. _`The Linux Journal`: http://www.linuxjournal.com
.. _`Work For Pie`: http://workforpie.com/


.. THIRD PARTY LIBS

.. _`mezzanine-html5boilerplate`: https://github.com/tvon/mezzanine-html5boilerplate
.. _`html5boilerplate project`: http://html5boilerplate.com/
.. _`mezzanine-mdown`: https://bitbucket.org/onelson/mezzanine-mdown
.. _`Markdown`: http://en.wikipedia.org/wiki/Markdown
.. _`mezzanine-openshift`: https://github.com/k4ml/mezzanine-openshift
.. _`Redhat's OpenShift`: https://openshift.redhat.com/
.. _`mezzanine-stackato`: https://github.com/Stackato-Apps/mezzanine
.. _`ActiveState's Stackato`: http://www.activestate.com/stackato
.. _`mezzanine-blocks`: https://github.com/renyi/mezzanine-blocks
.. _`mezzanine-widgets`: https://github.com/osiloke/mezzanine_widgets
.. _`mezzanine-themes`: https://github.com/renyi/mezzanine-themes
.. _`mezzanine-twittertopic`: https://github.com/lockhart/mezzanine-twittertopic
.. _`mezzanine-captcha`: https://github.com/mjtorn/mezzanine-captcha


.. PEOPLE WITH QUOTES

.. _`Van Lindberg`: http://www.lindbergd.info/
.. _`Antonio Rodriguez`: http://an.ton.io/
.. _`Jesse Noller`: http://jessenoller.com/
.. _`Emile Petrone`: https://twitter.com/emilepetrone
.. _`Audrey Roy`: http://cartwheelweb.com/
.. _`Michael Delaney`: http://github.com/fusepilot/
.. _`John Campbell`: http://head3.com/
.. _`Phil Hughes`: http://www.linuxjournal.com/blogs/phil-hughes
