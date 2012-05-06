==========
Deployment
==========

Deployment of a Mezzanine site to production is mostly identical to
deploying a regular Django site. For serving static content, Mezzanine
makes full use of Django's ``staticfiles`` app. For more information,
see the Django docs for
`deployment <https://docs.djangoproject.com/en/dev/howto/deployment/>`_ and
`staticfiles <https://docs.djangoproject.com/en/dev/howto/static-files/>`_.

Multiplie Sites and Multi-Tenancy
=================================

Mezzanine makes use of of Django's ``sites`` app to support multiple
sites in a single project. This functionality is always "turned on" in
Mezzanine: a single ``Site`` record always exists, and is referenced
when retrieving site related data, which most content in Mezzanine falls
under.

Where Mezzanine diverges from Django is how the ``Site`` record is
retrieved. Typically a running instance of a Django project is bound
to a single site defined by the ``SITE_ID`` setting, so while a project
may contain support for multiple sites, a separate running instance of
the project is required per site.

Mezzanine uses a pipeline of checks to determine which site to
reference when accessing content. The most import of these is one where
the host name of the current request is compared to the domain name
specified for each ``Site`` record. With this in place, true
multi-tenancy is achieved, and multiple sites can be hosted within a
single running instance of the project.

Here's the list of checks in the pipeline, in order:

  * The session variable ``site_id``. This allows a project to include
    features where a user's session is explicitly associated with a site.
    Mezzanine uses this in it's admin to allow admin users to switch
    between sites to manage, while accessing the admin on a single domain.
  * The domain matching the host of the current request, as described
    above.
  * The environment variable ``MEZZANINE_SITE_ID``. This allows
    developers to specify the site for contexts outside of a HTTP
    request, such as management commands. Mezzanine includes a custom
    ``manage.py`` which will check for (and remove) a ``--site=ID``
    argument.
  * Finally Mezzanine will fall back to the ``SITE_ID`` setting if none
    of the above checks can occur.

Twitter Feeds
=============

If Twitter feeds are implemented in your templates, a cron job is
required that will run the following management command::

    $ python manage.py poll_twitter

This ensures that the data is always available in the site's database
when accessed, and allows you to control how often the Twitter API is
queried.
