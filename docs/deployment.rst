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
  * `virtualenv <https://pypi.python.org/pypi/virtualenv>`_ - isolated Python
    environments for each project
  * `git <http://git-scm.com/>`_ or `mercurial <http://mercurial.selenic.com/>`_
    - version control systems (optional)

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

Configurable variables are implemented in the project's ``local_settings.py``
module. Here's an example, that leverages some existing setting names::

  # Domains for public site
  ALLOWED_HOSTS = ["example.com"]

  FABRIC = {
      "DEPLOY_TOOL": "rsync",  # Deploy with "git", "hg", or "rsync"
      "SSH_USER": "server_user",  # VPS SSH username
      "HOSTS": ["123.123.123.123"],  # The IP address of your VPS
      "DOMAINS": ALLOWED_HOSTS,  # Edit domains in ALLOWED_HOSTS
      "REQUIREMENTS_PATH": "requirements.txt",  # Project's pip requirements
      "LOCALE": "en_US.UTF-8",  # Should end with ".UTF-8"
      "DB_PASS": "",  # Live database password
      "ADMIN_PASS": "",  # Live admin user password
      "SECRET_KEY": SECRET_KEY,
      "NEVERCACHE_KEY": NEVERCACHE_KEY,
  }

Commands
--------

Here's the list of commands provided in a Mezzanine project's
``fabfile.py``. Consult the `Fabric documentation <http://fabfile.org>`_
for more information on working with these:

.. include:: fabfile.rst

Tutorial
========

CASE 1: Deploying to a brand new server
----------------------------------------

1. Get your sever. Anything that grants you root access works. VPS's like those
   from Digital Ocean work great and are cheap.
2. Fill the ``ALLOWED_HOSTS`` and ``FABRIC`` settings in ``local_settings.py``
   as shown in the `Configuration`_ section above. For ``SSH_USER`` provide any
   username you want (not root), and the fabfile will create it for you.
3. Run ``fab secure``. You simply need to know the root password to your VPS.
   The new user will be created and you can SSH with that from now on (if
   needed). For security reason, root login via SSH is disabled by this task.
4. Run ``fab all``. It will take a while to install the required environment,
   but after that, your Mezzanine site will be live.

Notice that not even once you had to manually SSH into your VPS. *Note: some
server providers (like Digital Ocean) require you to login as root once to
change the default password. It should be the only time you are required to SSH
into the sever.*

CASE 2: Deploying to an existing server
---------------------------------------

If you already have a server, and you already have created a non-root user with
sudo privileges:

1. Fill the ``ALLOWED_HOSTS`` and ``FABRIC`` settings in ``local_settings.py``
   as shown in the `Configuration`_ section above. For ``SSH_USER`` provide the
   user with sudo privileges.
2. Run ``fab install`` to install system-wide requirements.
3. Run ``fab deploy`` to deploy your project.
   
Deploying more than one site to the server
------------------------------------------

After you have completed your first deployment, for all subsequent deployments
in the same server (either new sites or updates to your existing sites) you only
need to run ``fab deploy``.

Fixing bugs pushed by accident to the server
--------------------------------------------

1. Run ``fab rollback``. This will roll back your project files, database, and
   static files to how they were in the last (working) deployment.
2. Work on the fixes in your development machine.
3. Run ``fab deploy`` to push your fixes to production.
