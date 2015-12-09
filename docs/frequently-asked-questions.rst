==========================
Frequently Asked Questions
==========================

These are some of the most frequently asked questions on the
`Mezzanine mailing list <http://groups.google.com/group/mezzanine-users>`_.

  * :ref:`prerequisites`
  * :ref:`static-files`
  * :ref:`wysiwyg-filtering`
  * :ref:`homepage`
  * :ref:`project-vs-app`
  * :ref:`templates`
  * :ref:`themes`
  * :ref:`not-invented-here`
  * :ref:`existing-projects`
  * :ref:`grappelli-filebrowser-forks`
  * :ref:`what-is-pillow`
  * :ref:`missing-features`
  * :ref:`cartridge-without-mezzanine`
  * :ref:`contributing`

.. _prerequisites:

What do I need to know to use Mezzanine?
----------------------------------------

First and foremost, Mezzanine is based on the `Django framework
<https://www.djangoproject.com/>`_. All aspects of working with
Mezzanine will benefit from a good understanding of how Django works.
Many questions that are asked within the Mezzanine
community can easily be answered by reading the `Django documentation
<https://docs.djangoproject.com/en/>`_.

Setting up a development environment, and deploying a Mezzanine site,
is the same process as doing so with a regular Django site. Areas such
as version control, installing Python packages, and setting up a web
server  such as `Apache <http://httpd.apache.org/>`_ or `NGINX
<http://nginx.org/>`_, will all be touched upon.

Modifying the look and feel of a Mezzanine powered site requires at
least an understanding of HTML, CSS and `Django's templating system
<https://docs.djangoproject.com/en/dev/topics/templates/>`_.

Extending Mezzanine by :ref:`creating-custom-content-types` or using
additional Django apps, will require some knowledge of programming with
`Python <http://python.org>`_, as well as a good understanding of
Django's components, such as
`models <https://docs.djangoproject.com/en/dev/topics/db/models/>`_,
`views <https://docs.djangoproject.com/en/dev/topics/http/views/>`_,
`urlpatterns <https://docs.djangoproject.com/en/dev/topics/http/urls/>`_
and the `admin <https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_.

`Back to top <#>`_

.. _static-files:

Why aren't my JavaScript and CSS files showing up?
--------------------------------------------------

Mezzanine makes exclusive use of `Django's staticfiles app
<https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_,
for managing static files such as JavaScript, CSS, and images.

When the ``DEBUG`` setting is set to ``True``, as it would be during
development, the URL defined by the setting ``STATIC_URL`` (usually
``/static/``), will host any files found in the ``static`` directory
of any application listed in the ``INSTALLED_APPS`` setting.

When ``DEBUG`` is set to ``False``, as it would be for your deployed
production site, you must run the ``collectstatic`` command on your
live site, which will copy all of the files from the ``static``
directory in each application, to the location defined by the
``STATIC_ROOT`` setting. You then need to configure an alias in your
web server's config (Apache, NGINX, etc) that maps the URL defined by
``STATIC_URL`` to serve files from this directory.

Long story short, Django doesn't serve static content when deployed in
production, leaving this up to the public facing web server, which is
absolutely the best tool for this job. Consult `Django's staticfiles
guide <https://docs.djangoproject.com/en/dev/howto/static-files/>`_
for more information.

`Back to top <#>`_

.. _wysiwyg-filtering:

Why does the WYSIWYG editor strip out my custom HTML?
-----------------------------------------------------

By default, Mezzanine strips out potentially dangerous HTML from
fields controlled by the WYSIWYG editor, such as tags and attributes
that could be used to inject JavaScript into a page. If this
didn't occur, a clever staff member could potentially add JavaScript
to a page, that when viewed by an administrator (a staff member with
superuser status), would cause the administrator's browser to post an
update via the admin, that updates the staff member's user account and
assigns them superuser status.

The above scenario is a fairly obscure one, so it's possible to
customise the level of filtering that occurs. Three levels of
filtering are implemented by default, that can be controlled in
the settings section of the admin. These are High (the default), Low
(which allows extra tags such as those required for embedding videos),
and None (no filtering occurs). This is implemented via the
:ref:`RICHTEXT_FILTER_LEVEL-LABEL` setting.

If your situation is one where your staff members are completely
trusted, and custom HTML within WYSIWYG fields is required, then you
can modify the filter level accordingly. Further customisation is
possible via the :ref:`RICHTEXT_ALLOWED_TAGS-LABEL`,
:ref:`RICHTEXT_ALLOWED_ATTRIBUTES-LABEL` and :ref:`RICHTEXT_ALLOWED_STYLES-LABEL`
settings, which can have extra allowed values appended to using
the ``append`` argument in Mezzanine's settings API. See the
:ref:`registering-settings` section for more information.

`Back to top <#>`_

.. _homepage:

Why isn't the homepage a Page object I can edit via the admin?
------------------------------------------------------------------

In our experience, the homepage of a beautiful, content driven website,
is quite different from other pages of the site, that all fall under
sets of repeatable page types. The homepage also differs greatly from
site to site. Given this, Mezzanine doesn't presume how your homepage
will be structured and managed. It's up to you to implement how it
works per site.

By default, the homepage provided with Mezzanine is a static template,
namely ``mezzanine/core/templates/index.html`` (or
``templates/index.html`` if stored directly in your project). You can
change the ``urlpattern`` for the homepage in your project's
``urls.py`` module. Be certain to take a look at the `urls.py module
<https://github.com/stephenmcd/mezzanine/tree/master/mezzanine/project_template/project_name/urls.py>`_,
as it contains several examples of different types of homepages.
In ``urls.py`` you'll find examples of pointing the homepage to a
:class:`.Page` object in the page tree, or pointing the homepage to the blog
post listing page, which is useful for sites that are primarily blogs.

Of course with Django's models, admin classes, and template tags, the
sky is the limit and you're free to set up the homepage to be managed
in any way you like.

`Back to top <#>`_

.. _project-vs-app:

Why is Mezzanine a Django project, and not a Django app?
--------------------------------------------------------

Mezzanine comes with many features that are related to content driven
websites, yet are quite distinct from each other. For example
user-built forms and blog posts are both common requirements for a
website, yet aren't particularly related to each other. So Mezzanine
as a whole is a collection of different Django apps, all packaged
together to work seamlessly.

Mezzanine provides its own `project template
<https://github.com/stephenmcd/mezzanine/tree/master/mezzanine/project_template>`_,
with ``settings.py`` and ``urls.py`` modules that configure all of
Mezzanine's apps, which you can (and should) modify per project.

`Back to top <#>`_

.. _templates:

Where are all the templates I can modify?
-----------------------------------------

Each of the templates Mezzanine provides can be found in the
``templates`` directory of each Django app that Mezzanine is comprised
of. Take the time to explore the structure of these, starting with the
base template ``mezzanine/core/templates/base.html`` (or
``templates/base.html`` if stored directly in your project) which is
the foundation for the entire site, going more granular as needed.

Once you're familiar with the templates you'd like to modify, copy them
into your project's ``templates`` directory and modify them there. You
can also use the ``collecttemplates`` command to copy templates over
automatically. Run ``python manage.py collecttemplates --help`` for
more info. Be mindful that this means the copied templates will always
be used, rather than the ones stored within Mezzanine itself, which is
something to keep in mind if you upgrade to a newer version of
Mezzanine.

`Back to top <#>`_

.. _themes:

How do I create/install a theme?
--------------------------------

Prior to version 1.0, Mezzanine had a set of features for creating
and installing themes. These mostly were in place to address handling
static files, since at that time Mezzanine was not integrated with
`Django's staticfiles app
<https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_.
Mezzanine 1.0 makes full use of ``staticfiles``, and so the theming
features were removed since they became redundant.

From that point on, a theme in Mezzanine can be implemented entirely
as a standard Django app. Simply create a Django app with
``templates`` and ``static`` directories, copy the relevant HTML,
CSS and JavaScript files into it from Mezzanine that you wish to
modify, and then add the theme app's name to your project's
``INSTALLED_APPS`` setting. Be sure to add the theme to the top of
the ``INSTALLED_APPS`` list, so that its templates are found before
Mezzanine's versions of the templates.

Have you created a cool theme that you'd like to share with the
community? Package your theme up and put it on `PyPI
<http://pypi.python.org/pypi>`_ and let us know via the `mailing list
<http://groups.google.com/group/mezzanine-users>`_- that way people
can automatically install it along with their Mezzanine project.

`Back to top <#>`_

.. _not-invented-here:

Why does Mezzanine contain its own [FEATURE] instead of using [PACKAGE]?
------------------------------------------------------------------------

To be honest you could implement most of Mezzanine's features by gluing
together dozens of smaller, stand-alone, open source Django apps.
Several larger Django site-building frameworks take this approach, and
it's a noble one. The downside to this is that a significant portion
of time on your project will be spent maintaining the glue between
these apps, as their development evolves independently from each other,
as well as from your project itself. At best you'll be able to work with
the apps' developers to ease this evolution, at worst you'll be stuck
hacking work-arounds for incompatibilities between the apps.

One of the core goals of Mezzanine is to avoid this situation, by
providing all of the features commonly required by content driven
sites, with just the right level of extensibility to customize your
Mezzanine powered site as required. By taking this approach, the team
behind Mezzanine is in complete control over its components, and can
ensure they work together seamlessly.

`Back to top <#>`_

.. _existing-projects:

How can I add Mezzanine to an existing Django project?
------------------------------------------------------

Mezzanine is a Django project made up of multiple Django apps, and is
geared towards being used as the basis for new Django projects, however
adding Mezzanine to an existing Django project should be as simple as
adding the necessary settings and urlpatterns.

Mezzanine contains a `project_template directory
<https://github.com/stephenmcd/mezzanine/tree/master/mezzanine/project_template>`_,
which it uses to create new projects. In here you'll find the
necessary ``settings.py`` and ``urls.py`` modules, containing the
project-level setup for Mezzanine. Of particular note are the following
settings:

  * ``INSTALLED_APPS``
  * ``TEMPLATE_CONTEXT_PROCESSORS``
  * ``MIDDLEWARE_CLASSES``
  * ``PACKAGE_NAME_GRAPPELLI`` and ``PACKAGE_NAME_FILEBROWSER`` (for
    `django-grappelli <https://github.com/sehmaschine/django-grappelli>`_ and
    `django-filebrowser <https://github.com/sehmaschine/django-filebrowser>`_
    integration)
  * The call to ``mezzanine.utils.conf.set_dynamic_settings`` at the
    very end of the ``settings.py`` module.

`Back to top <#>`_

.. _grappelli-filebrowser-forks:

Why are Grappelli and Filebrowser forked?
-----------------------------------------

`Grappelli <https://github.com/sehmaschine/django-grappelli>`_ and
`Filebrowser <https://github.com/sehmaschine/django-filebrowser>`_ are
fantastic Django apps, and Mezzanine's admin interface would be much
poorer without them. When Mezzanine was first created, both of these apps
had packaging issues that went unaddressed for quite some time.
Development of Mezzanine moved extremely quickly during its early days,
and so the forks `grappelli_safe <https://github.com/stephenmcd/grappelli-safe>`_
and `filebrowser_safe <https://github.com/stephenmcd/filebrowser-safe>`_
were created to allow Mezzanine to be packaged up and installed in a
single step.

Over time the packaging issues were resolved, but Grappelli and
Filebrowser took paths that weren't desired in Mezzanine.
They're only used in Mezzanine for skinning the admin, and providing
a generic media library. Extra features that have been added to
Grappelli and Filebrowser along the way, haven't been necessary for
Mezzanine.

Over time, small changes have also been made to the ``grappelli_safe``
and ``filebrowser_safe`` forks, in order to integrate them more closely
with Mezzanine. So to this day, the forks are still used as
dependencies. They're stable, and have relatively low activity.

`Back to top <#>`_

.. _what-is-pillow:

What is this Pillow dependency?
-------------------------------

Mezzanine makes use of `Python Imaging Library
<http://www.pythonware.com/products/pil/>`_ (PIL) for generating
thumbnails. Having PIL as a dependency that gets automatically
installed with Mezzanine has caused issues for some people, due to
certain issues with PIL's own packaging setup.

`Pillow <http://pypi.python.org/pypi/Pillow>`_ is simply a packaging
wrapper around PIL that addresses these issues, and ensures PIL is
automatically installed correctly when installing Mezzanine. Pillow is
only used when PIL is not already installed.

`Back to top <#>`_

.. _missing-features:

Why doesn't Mezzanine have [FEATURE]?
-------------------------------------

The best answer to this might be found by searching the `mailing
list <http://groups.google.com/group/mezzanine-users>`_, where many
features that aren't currently in Mezzanine have been thoroughly
discussed.

Sometimes the conclusion is that certain features aren't within the
scope of what Mezzanine aims to be. Sometimes they're great ideas, yet
no one has had the time to implement them yet. In the case of the
latter, the quickest way to get your feature added is to get working on
it yourself.

Communication via the mailing list is key though. Features have been
developed and rejected before, simply because they were relatively
large in size, and developed in a silo without any feedback from the
community. Unfortunately these types of contributions are difficult
to accept, since they have the greatest resource requirements in
understanding everything involved, without any previous communication.

`Back to top <#>`_

.. _cartridge-without-mezzanine:

Can I use Cartridge without Mezzanine?
--------------------------------------

No. `Cartridge <http://cartridge.jupo.org>`_ (an ecommerce app)
heavily leverages Mezzanine, and in fact it is implemented as an
advanced example of a Mezzanine content type, where each shop category
is a page in Mezzanine's navigation tree. This allows for a very
flexible shop structure, where hierarchical categories can be set up
to create your shop.

You could very well use Cartridge and Mezzanine to build a pure
Cartridge site, without using any of Mezzanine's features that
aren't relevant to Cartridge. However more often than not, you'll
find that general content pages and forms, will be required to some
extent anyway.

`Back to top <#>`_

.. _contributing:

I don't know how to code, how can I contribute?
-----------------------------------------------

You're in luck! Programming is by far the most abundant skill
contributed to Mezzanine, and subsequently the least needed. There are
many ways to contribute without writing any code:

  * Answering questions on the `mailing list
    <http://groups.google.com/group/mezzanine-users>`_
  * Triaging `issues on GitHub
    <https://github.com/stephenmcd/mezzanine/issues>`_
  * Improving the documentation
  * Promoting Mezzanine via blogs, `Twitter <http://twitter.com>`_, etc.

If you don't have time for any of these things, and still want to
contribute back to Mezzanine, donations are always welcome and can be
made via Flattr or PayPal on the `Mezzanine homepage <http://mezzanine.jupo.org>`_.
Donations help to support the continued development of Mezzanine, and go
towards paying for infrastructure, such as hosting for the demo site.

`Back to top <#>`_
