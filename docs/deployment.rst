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
