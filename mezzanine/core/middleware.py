
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.middleware.cache import UpdateCacheMiddleware
from django.middleware.cache import FetchFromCacheMiddleware

from mezzanine.conf import settings
from mezzanine.utils.device import device_from_request, templates_for_device


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
                next = request.GET.get("next", "/")
                admin_url = reverse("admin:index")
                if login_type == "admin" and not next.startswith(admin_url):
                    next = admin_url
                return HttpResponseRedirect(next)
            else:
                return response
        return None


class TemplateForDeviceMiddleware(object):

    def process_template_response(self, request, response):
        """
        Inserts device-specific templates to the template list.
        """
        templates = templates_for_device(request, response.template_name)
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

class SSLMiddleware(object):
    """
    Handles redirections required for SSL. If SITE_FORCE_HOST
    is set and is not the current host, redirect to it if
    SITE_SSL_ENABLED is True, and ensure checkout views are
    accessed over HTTPS and all other views are accessed over HTTP.
    """
    def process_request(self, request):
        settings.use_editable()
        force_host = settings.SITE_FORCE_HOST
        if force_host and request.get_host().split(":")[0] != force_host:
            url = "http://%s%s" % (force_host, request.get_full_path())
            return HttpResponsePermanentRedirect(url)
        if settings.SITE_SSL_ENABLED and not settings.DEV_SERVER:
            url = "%s%s" % (request.get_host(), request.get_full_path())
            if request.path.startswith(settings.SITE_FORCE_SSL_URL_PREFIXES):
                if not request.is_secure():
                    return HttpResponseRedirect("https://%s" % url)
            elif request.is_secure():
                return HttpResponseRedirect("http://%s" % url)

try:
    settings.SHOP_SSL_ENABLED
    import warnings
    warnings.warn("SHOP_SSL_ENABLED deprecated; "
                  "use SITE_SSL_ENABLED, "
                  "mezzanine.core.middleware.SSLMiddleware and "
                  "SITE_FORCE_SSL_URL_PREFIXES",)
except AttributeError:
    pass

try:
    settings.SHOP_FORCE_HOST
    import warnings
    warnings.warn("SHOP_FORCE_HOST deprecated; "
                  "use SITE_FORCE_HOST",)
except AttributeError:
    pass
