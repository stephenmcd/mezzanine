==========
Deployment
==========

Deployment of a Mezzanine site to production is mostly identical to
deploying a regular Django site. For serving static content, Mezzanine
makes full use of Django's ``staticfiles`` app. For more information,
see the Django docs for
`deployment <https://docs.djangoproject.com/en/dev/howto/deployment/>`_ and
`staticfiles <https://docs.djangoproject.com/en/dev/howto/static-files/>`_.

Multi-Site
==========

Mezzanine currently supports multi-site functionality through the use
of Django's ``sites`` app. This functionality is always "turned on" in
Mezzanine: a single-site deployment is a deployment of Mezzanine
that references a single ``Site`` record, which is how Mezzanine is
configured out of the box.

Migrating from a single-site deployment to a multi-site deployment is
simply a matter of adding another site to the ``sites`` application's
``Site`` table, and then creating a new instance of Django that
references that record via the ``SITE_ID`` setting in its ``settings``
module.

A multi-site Mezzanine deployment that supports three sites would be
configured as so:

  * A shared database will exist to store data for all three sites.
  * Three separate runtime instances of Django, each with its own
    settings.py file, will be created, each responsible for managing
    a single site.
  * Each settings.py file used by these three instances will point to
    a different ``Site`` record via the ``SITE_ID`` setting.
  * If the different sites use different themes or templates, then
    different ``INSTALLED_APPS`` can be specified for each of these
    three independant instances.
  * All three settings.py files will contain the same ``DATABASES``
    settings.

The content of each individual site will be editable via the admin
application, running within the instance serving that site. In other
words, the admin running at ``siteone.com/admin`` will allow the
content of ``siteone.com`` to be edited, while the admin running at
``sitetwo.com/admin`` will allow the content of ``sitetwo.com`` to be
edited.

For more information regarding the Django sites application, see the
`Django Sites documentation <http://docs.djangoproject.com/en/dev/ref/contrib/sites/>`:

Twitter Feeds
=============

If Twitter feeds are implemented in your templates, a cron job is
required that will run the following management command::

    $ python manage.py poll_twitter

This ensures that the data is always available in the site's database
when accessed, and allows you to control how often the Twitter API is
queried.
