from __future__ import unicode_literals
from future.utils import native_str

from django.contrib import admin
from django.contrib.auth import logout
from django.contrib.messages import error
from django.contrib.redirects.models import Redirect
from django.core.exceptions import MiddlewareNotUsed
from django.core.urlresolvers import reverse, resolve
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponsePermanentRedirect, HttpResponseGone)
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.template import Template, RequestContext
from django.utils.cache import get_max_age
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from mezzanine.conf import settings
from mezzanine.core.models import SitePermission
from mezzanine.core.management.commands.createdb import (DEFAULT_USERNAME,
                                                         DEFAULT_PASSWORD)
from mezzanine.utils.cache import (cache_key_prefix, nevercache_token,
                                   cache_get, cache_set, cache_installed)
from mezzanine.utils.device import templates_for_device
from mezzanine.utils.sites import current_site_id, templates_for_host
from mezzanine.utils.urls import next_url


_deprecated = {
    "AdminLoginInterfaceSelector": "AdminLoginInterfaceSelectorMiddleware",
    "DeviceAwareUpdateCacheMiddleware": "UpdateCacheMiddleware",
    "DeviceAwareFetchFromCacheMiddleware": "FetchFromCacheMiddleware",
}


class _Deprecated(object):
    def __init__(self, *args, **kwargs):
        from warnings import warn
        msg = "mezzanine.core.middleware.%s is deprecated." % self.old
        if self.new:
            msg += (" Please change the MIDDLEWARE_CLASSES setting to use "
                    "mezzanine.core.middleware.%s" % self.new)
        warn(msg)

for old, new in _deprecated.items():
    globals()[old] = type(native_str(old),
                          (_Deprecated,),
                          {"old": old, "new": new})


class AdminLoginInterfaceSelectorMiddleware(object):
    """
    Checks for a POST from the admin login view and if authentication is
    successful and the "site" interface is selected, redirect to the site.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        login_type = request.POST.get("mezzanine_login_interface")
        if login_type and not request.user.is_authenticated():
            response = view_func(request, *view_args, **view_kwargs)
            if request.user.is_authenticated():
                if login_type == "admin":
                    next = request.get_full_path()
                    username = request.user.get_username()
                    if (username == DEFAULT_USERNAME and
                            request.user.check_password(DEFAULT_PASSWORD)):
                        error(request, mark_safe(_(
                              "Your account is using the default password, "
                              "please <a href='%s'>change it</a> immediately.")
                              % reverse("user_change_password",
                                        args=(request.user.id,))))
                else:
                    next = next_url(request) or "/"
                return HttpResponseRedirect(next)
            else:
                return response
        return None


class SitePermissionMiddleware(object):
    """
    Marks the current user with a ``has_site_permission`` which is
    used in place of ``user.is_staff`` to achieve per-site staff
    access.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        has_site_permission = False
        if request.user.is_superuser:
            has_site_permission = True
        elif request.user.is_staff:
            lookup = {"user": request.user, "sites": current_site_id()}
            try:
                SitePermission.objects.get(**lookup)
            except SitePermission.DoesNotExist:
                admin_index = reverse("admin:index")
                if request.path.startswith(admin_index):
                    logout(request)
                    view_func = admin.site.login
                    extra_context = {"no_site_permission": True}
                    return view_func(request, extra_context=extra_context)
            else:
                has_site_permission = True
        request.user.has_site_permission = has_site_permission


class TemplateForDeviceMiddleware(object):
    """
    Inserts device-specific templates to the template list.
    """
    def process_template_response(self, request, response):
        if hasattr(response, "template_name"):
            if not isinstance(response.template_name, Template):
                templates = templates_for_device(request,
                    response.template_name)
                response.template_name = templates
        return response


class TemplateForHostMiddleware(object):
    """
    Inserts host-specific templates to the template list.
    """
    def process_template_response(self, request, response):
        if hasattr(response, "template_name"):
            if not isinstance(response.template_name, Template):
                templates = templates_for_host(request,
                    response.template_name)
                response.template_name = templates
        return response


class UpdateCacheMiddleware(object):
    """
    Response phase for Mezzanine's cache middleware. Handles caching
    the response, and then performing the second phase of rendering,
    for content enclosed by the ``nevercache`` tag.
    """

    def process_response(self, request, response):

        # Caching is only applicable for text-based, non-streaming
        # responses. We also skip it for non-200 statuses during
        # development, so that stack traces are correctly rendered.
        is_text = response.get("content-type", "").startswith("text")
        valid_status = response.status_code == 200
        streaming = getattr(response, "streaming", False)
        if not is_text or streaming or (settings.DEBUG and not valid_status):
            return response

        # Cache the response if all the required conditions are met.
        # Response must be marked for updating by the
        # ``FetchFromCacheMiddleware`` having a cache get miss, the
        # user must not be authenticated, the HTTP status must be OK
        # and the response mustn't include an expiry age, indicating it
        # shouldn't be cached.
        marked_for_update = getattr(request, "_update_cache", False)
        anon = hasattr(request, "user") and not request.user.is_authenticated()
        timeout = get_max_age(response)
        if timeout is None:
            timeout = settings.CACHE_MIDDLEWARE_SECONDS
        if anon and valid_status and marked_for_update and timeout:
            cache_key = cache_key_prefix(request) + request.get_full_path()
            _cache_set = lambda r: cache_set(cache_key, r.content, timeout)
            if callable(getattr(response, "render", None)):
                response.add_post_render_callback(_cache_set)
            else:
                _cache_set(response)

        # Second phase rendering for non-cached template code and
        # content. Split on the delimiter the ``nevercache`` tag
        # wrapped its contents in, and render only the content
        # enclosed by it, to avoid possible template code injection.
        token = nevercache_token()
        try:
            token = token.encode('utf-8')
        except AttributeError:
            pass
        parts = response.content.split(token)
        # Restore csrf token from cookie - check the response
        # first as it may be being set for the first time.
        csrf_token = None
        try:
            csrf_token = response.cookies[settings.CSRF_COOKIE_NAME].value
        except KeyError:
            try:
                csrf_token = request.COOKIES[settings.CSRF_COOKIE_NAME]
            except KeyError:
                pass
        if csrf_token:
            request.META["CSRF_COOKIE"] = csrf_token
        context = RequestContext(request)
        for i, part in enumerate(parts):
            if i % 2:
                part = Template(part).render(context).encode("utf-8")
            parts[i] = part
        response.content = b"".join(parts)
        response["Content-Length"] = len(response.content)
        if hasattr(request, '_messages'):
            # Required to clear out user messages.
            request._messages.update(response)
        return response


class FetchFromCacheMiddleware(object):
    """
    Request phase for Mezzanine cache middleware. Return a response
    from cache if found, othwerwise mark the request for updating
    the cache in ``UpdateCacheMiddleware``.
    """

    def process_request(self, request):
        if (cache_installed() and request.method == "GET" and
                not request.user.is_authenticated()):
            cache_key = cache_key_prefix(request) + request.get_full_path()
            response = cache_get(cache_key)
            # We need to force a csrf token here, as new sessions
            # won't receieve one on their first request, with cache
            # middleware running.
            csrf_mw_name = "django.middleware.csrf.CsrfViewMiddleware"
            if csrf_mw_name in settings.MIDDLEWARE_CLASSES:
                csrf_mw = CsrfViewMiddleware()
                csrf_mw.process_view(request, lambda x: None, None, None)
                get_token(request)
            if response is None:
                request._update_cache = True
            else:
                return HttpResponse(response)


class SSLRedirectMiddleware(object):
    """
    Handles redirections required for SSL when ``SSL_ENABLED`` is ``True``.

    If ``SSL_FORCE_HOST`` is ``True``, and is not the current host,
    redirect to it.

    Also ensure URLs defined by ``SSL_FORCE_URL_PREFIXES`` are redirect
    to HTTPS, and redirect all other URLs to HTTP if on HTTPS.
    """
    def process_request(self, request):
        settings.use_editable()
        force_host = settings.SSL_FORCE_HOST
        response = None
        if force_host and request.get_host().split(":")[0] != force_host:
            url = "http://%s%s" % (force_host, request.get_full_path())
            response = HttpResponsePermanentRedirect(url)
        elif settings.SSL_ENABLED and not settings.DEV_SERVER:
            url = "%s%s" % (request.get_host(), request.get_full_path())
            if request.path.startswith(settings.SSL_FORCE_URL_PREFIXES):
                if not request.is_secure():
                    response = HttpResponseRedirect("https://%s" % url)
            elif request.is_secure() and settings.SSL_FORCED_PREFIXES_ONLY:
                response = HttpResponseRedirect("http://%s" % url)
        if response and request.method == "POST":
            if resolve(request.get_full_path()).url_name == "fb_do_upload":
                # The handler for the flash file uploader in filebrowser
                # doesn't have access to the http headers Django will use
                # to determine whether the request is secure or not, so
                # in this case we don't attempt a redirect - note that
                # when /admin is restricted to SSL using Mezzanine's SSL
                # setup, the flash uploader will post over SSL, so
                # someone would need to explictly go out of their way to
                # trigger this.
                return
            # Tell the client they need to re-POST.
            response.status_code = 307
        return response


class RedirectFallbackMiddleware(object):
    """
    Port of Django's ``RedirectFallbackMiddleware`` that uses
    Mezzanine's approach for determining the current site.
    """

    def __init__(self):
        if "django.contrib.redirects" not in settings.INSTALLED_APPS:
            raise MiddlewareNotUsed

    def process_response(self, request, response):
        if response.status_code == 404:
            lookup = {
                "site_id": current_site_id(),
                "old_path": request.get_full_path(),
            }
            try:
                redirect = Redirect.objects.get(**lookup)
            except Redirect.DoesNotExist:
                pass
            else:
                if not redirect.new_path:
                    response = HttpResponseGone()
                else:
                    response = HttpResponsePermanentRedirect(redirect.new_path)
        return response
