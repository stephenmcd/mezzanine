
Multi-Tenancy
=============

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
reference when accessing content. The most important of these is the one where
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

Per-site Themes
---------------

Consider a project for an organization or business with several related
domains that are to be managed by the same people, or for which sharing
of resources is a big benefit. These related domains can share the same
Django process, which can offer easier management and reduced resource
needs in the server environment.

The domains involved could have a direct subsidiary relationship, as
with example.com and several subdomains, or they may be completely
separate domains, as with example.com, example2.com, example3.com.
Either way, the domains are different hosts to which themes may be independently associated using the ``HOST_THEMES`` setting::

    # For a main domain and several subdomains.
    HOST_THEMES = [('example.com', 'example_theme'),
                   ('something.example.com', 'something_theme'),
                   ('somethingelse.example.com', 'somethingelse_theme')]

    # or for separate domains,
    HOST_THEMES = [('www.example.com', 'example_theme'),
                   ('example.com', 'example_theme'),
                   ('www.example2.com', 'example2_theme'),
                   ('www.example3.com', 'example3_theme')]

In either ``HOST_THEMES`` example above, there are three themes. Let's
continue with the second case, for example.com, example2.com, and
example3.com, for which there are three theme apps constructed:
``example_theme``, ``example2_theme``, and ``example3_theme``. The
following treatment illustrates a kind of theme inheritance across the
domains, with ``example_theme`` serving as the "base" theme.
Suppose ``example_theme`` contains a dedicated page content type
(see :ref:`creating-custom-content-types`), we'll call it the
``HomePage``, which is given a model definition in
``example_theme/models.py``, along with any other theme-related custom
content definitions.

Here is the layout for ``example_theme``, the "base" theme in this
arrangement::

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

The second and third themes, ``example2_theme`` and ``example3_theme``,
could be just as expansive, or they could be much simplified, as shown
by this layout for ``example2_theme`` (``example3_theme`` could be
identical)::

    /example2_theme
        /templates
            /pages
                /index.html <-- for the HomePage content type

Each theme would be listed under the ``INSTALLED_APPS`` setting, with
the "base" theme, ``example_theme``, listed first.

The project's main ``urls.py`` would need the following line active,
so that "/" is the target URL Mezzanine finds for home page rendering
(via the ``HomePage`` content type)::

    url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),

Mezzanine will look for a page instance at '/' for each theme.
``HomePage`` instances would be created via the admin system for each
site, and given the URL of '/' under the "Meta data" URL field. (Log
in to /admin, pick each site, in turn, creating a ``HomePage`` instance,
and editing the "Meta data" URL of each).

Although these aren't the only commands involved, they are useful
during the development process::

 * ``python manage.py startapp theme`` - start a theme; add/edit files
   next; add to INSTALLED_APPS before restart
 * ``python manage.py syncdb --migrate`` - after changes to themes;
   could require writing migrations
 * ``python manage.py collectstatic`` - gather static resources from the
   themes on occasion

Finally, under /admin, these sites will share some resources, such as
the media library, while there is separation of content stored in the
database (independent ``HomePage`` instances, independant blog posts,
an independent page hierarchy, etc.). Furthermore, the content types
added to, say ``example_theme``, e.g. ``HomePage``, are shared and
available in the different sites. Such nuances of sharing must be
considered when employing this approach.
