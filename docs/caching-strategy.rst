================
Caching Strategy
================

Mezzanine takes great care to ensure as few database queries as
possible are used, so that it performs well without any caching
configured. So while implementing caching for your Mezzanine
site is not a requirement, it is certainly well supported, as
Mezzanine comes pre-configured to aggressively cache content when
deployed to a production site with a cache backend installed.

.. note::

    By using Mezzanine's bundled deployment tools, Mezzanine's
    caching will be configured and in use for your production site.
    Consult the :doc:`deployment` section for more information.
    If you would like to have a cache backend configured but
    use a different caching strategy, simply removed the cache
    middleware described next.

Cache Middleware
================

Mezzanine's caching takes a hybrid approach drawing from several
popular caching techniques, combining them into one overall
implementation. Mezzanine provides its own implementation of
`Django's page-level cache middleware
<https://docs.djangoproject.com/en/dev/topics/cache/#the-per-site-cache>`_,
and behaves in a similar way.

Pages are fetched from cache by
``mezzanine.core.middleware.FetchFromCacheMiddleware``, which should
be at the end of the ``MIDDLEWARE_CLASSES`` setting, so that it is run
at the end of the request phase. If a cache miss occurs, the request
is marked as requiring a cache update, which is handled by
``mezzanine.core.middleware.UpdateCacheMiddleware``, which should be
at the start of ``MIDDLEWARE_CLASSES``, so that it is run at the end
of the response phase.

Mezzanine's cache middleware differs from its Django counterpart in
a few subtle yet significant ways:

  * Setting ``CACHE_ANONYMOUS_ONLY`` to ``False`` has no effect, so
    authenticated users never use the cache system.
  * Cache keys include the ID for the current Django ``Site`` object,
    and device (see :doc:`device-handling`).
  * Cache keys do not take Vary headers into account, so all
    unauthenticated visitors will receive the same page content per
    URL.

Two-Phased Rendering
====================

One approach to caching Django sites is to use `template fragment
caching <https://docs.djangoproject.com/en/dev/topics/cache/#template-fragment-caching>`_.
This is where we define the areas of templates that should be cached.
Two-phased rendering is the opposite of this approach. By default all
content is cached, and we then go back and define the sections of a
template that should never be cached. These areas would be anything
that makes use of the current request object, including session
specific data.

Mezzanine provides the start and end template tags ``nevercache`` and
``endnevercache``. Wrapping content in these tags will ensure the
enclosed content does not get cached. Two-phased rendering is where
the page is cached without any of the template code inside
``nevercache`` and ``endnevercache`` executed for the first phase.
The second phase then occurs after the page is retrieved from cache
(or not), and any template code inside ``nevercache`` and
``endnevercache`` is then executed.

Mezzanine's two-phased rendering is based on Cody Soyland's
`django-phased <https://github.com/codysoyland/django-phased>`_ and
Adrian Holovaty's `blog post
<http://www.holovaty.com/writing/django-two-phased-rendering/>`_ which
originally described the technique.

.. note::

    The template code inside ``nevercache`` and ``endnevercache`` will
    only have access to template tags and variables provided by a
    normal request context. This excludes any variables passed to the
    template from a view function. Variables added via context
    processors such as the current request, and Mezzanine's settings
    will be available. Template tag libraries should be loaded inside
    these areas of content in order to make use of their template tags.

Mint Cache
==========

The final step in Mezzanine's caching strategy is a technique known as
mint caching. This is where the expiry value for any cache entry is
stored in cache along with the cache entry itself. The real expiry
value used is the given expiry, plus the value defined by Mezzanine's
``CACHE_SET_DELAY_SECONDS`` setting. Each time a cache entry is
requested, the original expiry time is checked against, and if past,
the stale cache entry is put back into cache, along with a new expiry
time using the value of ``CACHE_SET_DELAY_SECONDS``. In this case, no
cache entry is returned, essentially faking a cache miss, so that the
caller can know to re-generate the cache entry. This ensures that real
cache misses never actually occur, so almost only one client will ever
perform regeneration of a cache entry.

Mezzanine's mint cache is based on `this snippet
<http://djangosnippets.org/snippets/793/>`_ created by
`Disqus <http://disqus.com>`_.

