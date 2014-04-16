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
module. Here's an example, that leverages some existing setting names::

  FABRIC = {
      "SSH_USER": "", # SSH username for host deploying to
      "HOSTS": ALLOWED_HOSTS[:1], # List of hosts to deploy to (eg, first host)
      "DOMAINS": ALLOWED_HOSTS, # Domains for public site
      "REPO_URL": "ssh://hg@bitbucket.org/user/project", # Project's repo URL
      "VIRTUALENV_HOME":  "", # Absolute remote path for virtualenvs
      "PROJECT_NAME": "", # Unique identifier for project
      "REQUIREMENTS_PATH": "requirements.txt", # Project's pip requirements
      "GUNICORN_PORT": 8000, # Port gunicorn will listen on
      "LOCALE": "en_US.UTF-8", # Should end with ".UTF-8"
      "DB_PASS": "", # Live database password
      "ADMIN_PASS": "", # Live admin user password
      "SECRET_KEY": SECRET_KEY,
      "NEVERCACHE_KEY": NEVERCACHE_KEY,
  }

Commands
--------

Here's the list of commands provided in a Mezzanine project's
``fabfile.py``. Consult the `Fabric documentation <http://fabfile.org>`_
for more information on working with these:

.. include:: fabfile.rst
