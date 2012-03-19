
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.middleware.cache import UpdateCacheMiddleware
from django.middleware.cache import FetchFromCacheMiddleware

from mezzanine.conf import settings
from mezzanine.utils.device import device_from_request, templates_for_device
from mezzanine.utils.sites import templates_for_host


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
                next = request.GET.get("next", request.get_full_path())
                admin_url = reverse("admin:index")
                if login_type == "admin" and not next.startswith(admin_url):
                    next = admin_url
                return HttpResponseRedirect(next)
            else:
                return response
        return None


class AdminLoginInterfaceSelector(AdminLoginInterfaceSelectorMiddleware):
    def __init__(self):
        import warnings
        old = "mezzanine.core.middleware.AdminLoginInterfaceSelector"
        warnings.warn("%s is deprecated. Please change the MIDDLEWARE_CLASSES "
                      "setting to use %sMiddleware" % (old, old))


class TemplateForDeviceMiddleware(object):

    def process_template_response(self, request, response):
        """
        Inserts device-specific templates to the template list.
        """
        templates = templates_for_device(request, response.template_name)
        response.template_name = templates
        return response


class TemplateForHostMiddleware(object):

    def process_template_response(self, request, response):
        """
        Inserts host-specific templates to the template list.
        """
        templates = templates_for_host(request, response.template_name)
        response.template_name = templates
        return response


class DeviceAwareCacheMiddleware(object):
    """
    Mixin for device-aware cache middleware that provides the method for
    prefixing the cache key with a device.
    """
    def set_key_prefix_for_device(self, request):
        device = device_from_request(request)
        self.key_prefix = "%s-%s" % (device,
                                     settings.CACHE_MIDDLEWARE_KEY_PREFIX)


class DeviceAwareUpdateCacheMiddleware(DeviceAwareCacheMiddleware,
                                       UpdateCacheMiddleware):
    """
    Device-aware version of Django's ``UpdateCacheMiddleware`` - prefixes
    the internal cache key with the device for the request for each response.
    """
    def process_response(self, request, response):
        self.set_key_prefix_for_device(request)
        return super(DeviceAwareUpdateCacheMiddleware,
                     self).process_response(request, response)


class DeviceAwareFetchFromCacheMiddleware(DeviceAwareCacheMiddleware,
                                          FetchFromCacheMiddleware):
    """
    Device-aware version of Django's ``FetchFromCacheMiddleware`` - prefixes
    the internal cache key with the device for the request for each request.
    """
    def process_request(self, request):
        self.set_key_prefix_for_device(request)
        return super(DeviceAwareFetchFromCacheMiddleware,
                     self).process_request(request)


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
        if force_host and request.get_host().split(":")[0] != force_host:
            url = "http://%s%s" % (force_host, request.get_full_path())
            return HttpResponsePermanentRedirect(url)
        if settings.SSL_ENABLED and not settings.DEV_SERVER:
            url = "%s%s" % (request.get_host(), request.get_full_path())
            if request.path.startswith(settings.SSL_FORCE_URL_PREFIXES):
                if not request.is_secure():
                    return HttpResponseRedirect("https://%s" % url)
            elif request.is_secure():
                return HttpResponseRedirect("http://%s" % url)
