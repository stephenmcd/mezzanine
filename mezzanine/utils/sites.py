import os
import sys
import threading
from contextlib import contextmanager

from django.contrib.sites.models import Site

from mezzanine.conf import settings
from mezzanine.core.request import current_request
from mezzanine.utils.conf import middlewares_or_subclasses_installed

SITE_PERMISSION_MIDDLEWARE = "mezzanine.core.middleware.SitePermissionMiddleware"


def current_site_id():
    """
    Responsible for determining the current ``Site`` instance to use
    when retrieving data for any ``SiteRelated`` models. If we're inside an
    override_current_site_id context manager, return the overriding site ID.
    Otherwise, try to determine the site using the following methods in order:

      - ``site_id`` in session. Used in the admin so that admin users
        can switch sites and stay on the same domain for the admin.
      - The id of the Site object corresponding to the hostname in the current
        request. This result is cached.
      - ``MEZZANINE_SITE_ID`` environment variable, so management
        commands or anything else outside of a request can specify a
        site.
      - ``SITE_ID`` setting.

    If a current request exists and the current site is not overridden, the
    site ID is stored on the request object to speed up subsequent calls.
    """

    if hasattr(override_current_site_id.thread_local, "site_id"):
        return override_current_site_id.thread_local.site_id

    from mezzanine.utils.cache import cache_get, cache_installed, cache_set

    request = current_request()
    site_id = getattr(request, "site_id", None)
    if request and not site_id:
        site_id = request.session.get("site_id", None)
        if not site_id:
            domain = request.get_host().lower()
            if cache_installed():
                # Don't use Mezzanine's cache_key_prefix here, since it
                # uses this very function we're in right now to create a
                # per-site cache key.
                bits = (settings.CACHE_MIDDLEWARE_KEY_PREFIX, domain)
                cache_key = "%s.site_id.%s" % bits
                site_id = cache_get(cache_key)
            if not site_id:
                try:
                    site = Site.objects.get(domain__iexact=domain)
                except Site.DoesNotExist:
                    pass
                else:
                    site_id = site.id
                    if cache_installed():
                        cache_set(cache_key, site_id)
    if not site_id:
        site_id = os.environ.get("MEZZANINE_SITE_ID", settings.SITE_ID)
    if request and site_id and not getattr(settings, "TESTING", False):
        request.site_id = site_id
    return site_id


@contextmanager
def override_current_site_id(site_id):
    """
    Context manager that overrides the current site id for code executed
    within it. Used to access SiteRelated objects outside the current site.
    """
    override_current_site_id.thread_local.site_id = site_id
    try:
        yield
    except Exception:
        raise
    finally:
        del override_current_site_id.thread_local.site_id


override_current_site_id.thread_local = threading.local()


def has_site_permission(user):
    """
    Checks if a staff user has staff-level access for the current site.
    The actual permission lookup occurs in ``SitePermissionMiddleware``
    which then marks the request with the ``has_site_permission`` flag,
    so that we only query the db once per request, so this function
    serves as the entry point for everything else to check access. We
    also fall back to an ``is_staff`` check if the middleware is not
    installed, to ease migration.
    """
    if not middlewares_or_subclasses_installed([SITE_PERMISSION_MIDDLEWARE]):
        return user.is_staff and user.is_active
    return getattr(user, "has_site_permission", False)


def host_theme_path():
    """
    Returns the directory of the theme associated with the given host.
    """

    # Set domain to None, which we'll then query for in the first
    # iteration of HOST_THEMES. We use the current site_id rather
    # than a request object here, as it may differ for admin users.
    domain = None

    for (host, theme) in settings.HOST_THEMES:
        if domain is None:
            domain = Site.objects.get(id=current_site_id()).domain
        if host.lower() == domain.lower():
            try:
                __import__(theme)
                module = sys.modules[theme]
            except ImportError:
                pass
            else:
                return os.path.dirname(os.path.abspath(module.__file__))
    return ""
