================
Caching Strategy
================

Mezzanine takes great care to appropriately minimize database queries.
This strategy enables Mezzanine to perform well without a caching
configuration. However, caching is also well-supported in the event
that you wish to implement customized caching for your Mezzanine site.
Mezzanine is preconfigured to cache aggressively when deployed to a
production site with a cache backend installed.

.. note::

    By using Mezzanine's bundled deployment tools, Mezzanine's caching
    will be properly configured and in use for your production site.
    Consult the :doc:`deployment` section for more information. If you
    would like to have a cache backend configured but to use a
    different caching strategy, simply remove the cache middleware
    described in the next section.

Cache Middleware
================

Mezzanine's caching system employs a hybrid approach which draws from
several popular caching techniques and combines them into one overall
implementation. Mezzanine provides its own implementation of `Django's
page-level cache middleware
<https://docs.djangoproject.com/en/dev/topics/cache/#the-per-site-
cache>`_, and behaves in a similar way.

Pages are fetched from cache by
:class:`mezzanine.core.middleware.FetchFromCacheMiddleware`, which should
appear at the end of the ``MIDDLEWARE_CLASSES`` setting and therefore
be activated at the end of the request phase. If a cache miss occurs,
the request is marked as requiring a cache update, which is handled by
:class:`mezzanine.core.middleware.UpdateCacheMiddleware`, which in turn
should appear at the start of ``MIDDLEWARE_CLASSES`` and therefore
be activated at the end of the response phase.

Mezzanine's cache middleware differs from its Django counterpart in
a few subtle yet significant ways:

  * Setting ``CACHE_ANONYMOUS_ONLY`` to ``False`` will have no effect,
    so authenticated users will never use the cache system.
  * Cache keys include the ID for the current Django ``Site`` object,
    and device (see :doc:`device-handling`).
  * Cache keys do not take Vary headers into account, so all
    unauthenticated visitors will receive the same page content per
    URL.

Two-Phased Rendering
====================

One approach to caching Django sites is to use `template fragment
caching <https://docs.djangoproject.com/en/dev/topics/cache/#template-
fragment-caching>`_, which defines the areas of templates to be
cached. Another approach is two-phased rendering, which is the
opposite. Using this method, all content is cached by default. We then
define the sections of a template that should not be cached. These
sections might be anything that makes use of the current request
object, including session-specific data.

Accordingly, Mezzanine provides the start and end template tags
:func:`.nevercache` and ``endnevercache``. Content wrapped in these tags
will not be cached. With two-phased
rendering, the page is cached without any of the template code
inside :func:`.nevercache` and ``endnevercache`` executed for the first
phase. The second phase then occurs after the page is retrieved from
cache (or not), and any template code inside :func:`.nevercache` and
``endnevercache`` is then executed.

Mezzanine's two-phased rendering is based on Cody Soyland's
`django-phased <https://github.com/codysoyland/django-phased>`_ and
Adrian Holovaty's `blog post
<http://www.holovaty.com/writing/django-two-phased-rendering/>`_ which
originally described the technique.

.. note::

    The template code inside :func:`.nevercache` and ``endnevercache`` will
    only have access to template tags and variables provided by a
    normal request context, with the exception of any variables passed
    to the template from a view function. Variables added via context
    processors such as the current request and via Mezzanine's
    settings will be available. Template tag libraries should be
    loaded inside these areas of content so as to make use of their
    template tags.

Mint Cache
==========

The final step in Mezzanine's caching strategy involves a technique
known as mint caching, in which the expiry value for any cache entry
is stored in cache along with the cache entry itself. The real expiry
value used is the given expiry plus the value defined by Mezzanine's
:ref:`CACHE_SET_DELAY_SECONDS-LABEL` setting. Each time a cache entry is
requested, the original expiry time is checked, and, if the expiry
time has passed, the stale cache entry is placed back into the cache
along with a new expiry time using the value of
:ref:`CACHE_SET_DELAY_SECONDS-LABEL`. In this case, no cache entry is returned,
which has the effect of essentially faking a cache miss, so that the
caller can know to regenerate the cache entry. This approach ensures
that cache misses never actually occur and that (almost) only one
client will ever perform regeneration of a cache entry.

Mezzanine's mint cache is based on `this snippet
<http://djangosnippets.org/snippets/793/>`_ created by
`Disqus <http://disqus.com>`_.
