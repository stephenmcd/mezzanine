
from django.http import HttpResponseRedirect
from django.middleware.cache import UpdateCacheMiddleware
from django.middleware.cache import FetchFromCacheMiddleware

from mezzanine.conf import settings
from mezzanine.utils.device import device_from_request


class MobileTemplate(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        import warnings
        warnings.warn("mezzanine.core.middleware.MobileTemplate is deprecated."
                      "Please remove it from settings.MIDDLEWARE_CLASSES.",
                      DeprecationWarning)
        return None


class AdminLoginInterfaceSelector(object):
    """
    Checks for a POST from the admin login view and if authentication is
    successful and the "site" interface is selected, redirect to the site.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        site_login = request.POST.get("mezzanine_login_interface") == "site"
        if site_login and not request.user.is_authenticated():
            response = view_func(request, *view_args, **view_kwargs)
            if request.user.is_authenticated():
                return HttpResponseRedirect(request.GET.get("next", "/"))
            else:
                return response
        return None

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
