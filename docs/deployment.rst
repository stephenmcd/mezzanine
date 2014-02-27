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

Configuration
-------------

Consider a project for an organization or business with several related domains
that are to be managed by the same people, or for which sharing of
resources is a big benefit. These related domains can share the same Django
process, which can offer easier management and reduced resource needs in the
server environment.

The domains involved could have a direct subsidiary relationship, as with
example.com and several subdomains, or they may be completely separate domains,
as with example.com, example2.com, example3.com. Either way, the domains are
different hosts to which themes may be independently associated using the
HOST_THEMES setting::

    for a main domain and several subdomains,

    HOST_THEMES = [('example.com', 'example_theme'),
                   ('something.example.com', 'something_theme'),
                   ('somethingelse.example.com', 'somethingelse_theme')]

    or for separate domains,

    HOST_THEMES = [('www.example.com', 'example_theme'),
                   ('example.com', 'example_theme'),
                   ('www.example2.com', 'example2_theme'),
                   ('www.example3.com', 'example3_theme')]

It may be necessary to add rewrite rules to handle use of www and non-www
domains, or some other combinations. For example, in nginx configuration, the
following lines would work to rewrite a non-www domain to a www domain, as used
in the example for separate domains::

    server {
        server_name example2.com;
        return 301 $scheme://www.example2.com$request_uri;
    }

    server {
        listen 80;
        listen 443 default ssl;
        server_name example.com www.example.com www.example2.com www.example3.com;
        ...
    }

In the first server block we rewrite example2.com to www.example2.com so that
the host name is forced to the www variant, ready for differentiation in
Mezzanine via the HOST_THEMES setting. In the second server block, we have the
domains involved listed in the server_name directive.

In either HOST_THEMES example above, there are three themes. Let's continue
with the second case, for example.com, example2.com, and example3.com, for
which there are three theme apps constructed: example_theme, example2_theme,
and example3_theme. The following treatment illustrates a kind of theme
inheritance across the domains, with example_theme serving as the "base" theme.
example_theme contains a dedicated page content type, HomePage, which is given
a model definition in example_theme/models.py, along with any other
theme-related custom content definitions.

Here is the layout for example_theme, the "base" theme in this arrangement::

    /example_theme
        admin.py
        models.py <-- has a HomePage type, subclassing Page
        ...
        /static
            /css
            /img
            /js
        /templates
            /base.html <-- used by this and the other two themes
            /pages
                /index.html <-- for the HomePage content type
        /templatetags
            some_tags.py <-- for code supporting HomePage functionality

The second and third themes, example2_theme and example3_theme, could be just
as expansive, or they could be much simplified, as shown by this layout for
example2_theme (example3_theme could be identical)::

    /example2_theme
        /templates
            /pages
                /index.html <-- for the HomePage content type

Each theme would be listed under the INSTALLED_APPS setting, with the
"base" theme, example_theme, listed first.

The main project urls.py would need the following line active, so that "/" is
the target URL Mezzanine finds for home page rendering (via the HomePage
content type)::

    url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),

Mezzanine will look for a page instance at '/' for each theme.  HomePage
instances would be created via the Admin system for each site, and given the
URL of '/' under the ``Meta data`` URL field. (Log in to /admin, pick each
site, in turn, creating a HomePage instance, and editing the ``Meta data`` URL
of each).

Although these aren't the only commands involved, they are useful during the
development process::

    python manage.py startapp theme <-- start a theme; add/edit files next;
                                        add to INSTALLED_APPS before restart

    python manage.py syncdb --migrate <-- after changes to themes; could
                                          require writing migrations

    python manage.py collectstatic <-- gather static resources from the themes
                                       on occasion

Finally, under /admin, these sites will share some resources, such as the media
library, while there is separation of content stored in the database
(independent HomePage instances, independant blog posts, an independent page
hierarchy, etc.).  Furthermore, the content types added to, say example_theme,
e.g. HomePage, are shared and available in the different sites. Such nuances of
sharing must be considered when employing this approach.

Use of SSL with Multiple Sites [PERHAPS OMIT]
------------------------------

In scenarios like those above, there may be a need for an online shop, which
requires a security certificate and SSL configuration.  To save money, only one
shop could be used, on the main domain. This would require only one security
certificate, with the other two websites linking into it.  Several settings may
prove useful. In the second example above, we might have the shop on
example.com, and we may have purchased the security certificate explicitly for
www.example.com. In this case, we could configure as follows::

    SSL_ENABLED = True
    #SSL_FORCE_HOST = "www.example.com"
    SSL_FORCE_URL_PREFIXES = (u'/admin', u'/account', u'/shop/checkout')

[FIXME: The second line is commented out, because the forcing triggered by this
setting interferes with the mapping done via HOST_THEMES. Perhaps this has to
do with the order that middleware processes happen?]

Virtual server configurations are commonly used to host multiple sites on a
single server, perhaps with several Mezzanine-Django-gunicorn processes running
behind nginx, as the default Mezzanine fabric script prepares. If there is only
one Cartridge shop in the mix, then the server hosting the shop can be
configured as the default. However, when there are multiple sites with shops,
something more advanced is needed, such as adding support for multiple IP
addresses on the same server, or using Server Name Indication, which allows
multiple secure websites to be served off the same IP address without requiring
use of a single certificate.

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

Caveats:

I haven't actually tried this with subdomains.
