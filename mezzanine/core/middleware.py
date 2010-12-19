
from django.http import HttpResponseRedirect


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
