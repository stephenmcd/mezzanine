==========
Deployment
==========

Deployment of a Mezzanine site to production is mostly identical to
deploying a regular Django site. For serving static content, Mezzanine
makes full use of Django's ``staticfiles`` app. For more information,
see the Django docs for
`deployment <https://docs.djangoproject.com/en/dev/howto/deployment/>`_ and
`staticfiles <https://docs.djangoproject.com/en/dev/howto/static-files/>`_.

Fabric
======

Each Mezzanine project comes bundled with utilities for deploying
production Mezzanine sites, using `Fabric <http://fabfile.org>`_.
The provided ``fabfile.py`` contains composable commands that can be
used to set up all the system-level requirements on a new
`Debian <http://debian.org>`_ based system, manage each of the
project-level virtual environments for initial and continuous
deployments, and much more.

Server Stack
------------

The deployed stack consists of the following components:

  * `NGINX <http://nginx.org>`_ - public facing web server
  * `gunicorn <http://gunicorn.org>`_ - internal HTTP application server
  * `PostgreSQL <http://postgresql.org>`_ - database server
  * `memcached <http://memcached.org>`_ - in-memory caching server
  * `supervisord <http://supervisord.org>`_ - process control and monitor

.. note::

  None of the items listed above are required for deploying Mezzanine,
  they're simply the components that have been chosen for use in the
  bundled ``fabfile.py``. Alternatives such as `Apache
  <http://httpd.apache.org/>`_ and `MySQL <http://www.mysql.com/>`_
  will work fine, but you'll need to take care of setting these up
  and deploying yourself. Consult the Django documentation for more
  information on using different `web
  <https://docs.djangoproject.com/en/dev/howto/deployment/>`_ and
  `database <https://docs.djangoproject.com/en/dev/ref/databases/>`_
  servers.

Configuration
-------------

Configurable variables are implemented in the project's ``settings.py``
module. Here's an example::

  FABRIC = {
      "SSH_USER": "", # SSH username
      "SSH_PASS":  "", # SSH password (consider key-based authentication)
      "SSH_KEY_PATH":  "", # Local path to SSH key file, for key-based auth
      "HOSTS": [], # List of hosts to deploy to
      "VIRTUALENV_HOME":  "", # Absolute remote path for virtualenvs
      "PROJECT_NAME": "", # Unique identifier for project
      "REQUIREMENTS_PATH": "requirements/project.txt", # Path to pip requirements, relative to project
      "GUNICORN_PORT": 8000, # Port gunicorn will listen on
      "LOCALE": "en_US.utf8", # Should end with ".utf8"
      "LIVE_HOSTNAME": "www.example.com", # Host for public site.
      "REPO_URL": "", # Git or Mercurial remote repo URL for the project
      "DB_PASS": "", # Live database password
      "ADMIN_PASS": "", # Live admin user password
  }

Commands
--------

Here's the list of commands provided in a Mezzanine project's
``fabfile.py``. Consult the `Fabric documentation <http://fabfile.org>`_
for more information on working with these:

.. include:: fabfile.rst

Multiple Sites and Multi-Tenancy
=================================

Mezzanine makes use of Django's ``sites`` app to support multiple
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
    Mezzanine uses this in its admin to allow admin users to switch
    between sites to manage, while accessing the admin on a single domain.
  * The domain matching the host of the current request, as described
    above.
  * The environment variable ``MEZZANINE_SITE_ID``. This allows
    developers to specify the site for contexts outside of a HTTP
    request, such as management commands. Mezzanine includes a custom
    ``manage.py`` which will check for (and remove) a ``--site=ID``
    argument.
  * Finally, Mezzanine will fall back to the ``SITE_ID`` setting if none
    of the above checks can occur.

Twitter Feeds
=============

If Twitter feeds are implemented in your templates, a cron job is
required that will run the following management command. For example,
if we want the tweets to be updated every 10 minutes::

    */10 * * * * python path/to/your/site/manage.py poll_twitter

This ensures that the data is always available in the site's database
when accessed, and allows you to control how often the Twitter API is
queried. Note that the Fabric script described earlier includes
features for deploying templates for cron jobs, which includes the
job for polling Twitter by default.

As of June 2013, Twitter also requires that all API access is
authenticated. For this you'll need to configure OAuth credentials for
your site to access the Twitter API. These settings are configurable
as Mezzanine settings. See the :doc:`configuration` section for more
information on these, as well as the `Twitter developer site
<https://dev.twitter.com/>`_ for info on configuring your OAuth
credentials.
