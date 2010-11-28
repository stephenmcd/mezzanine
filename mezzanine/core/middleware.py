
from django.contrib.admin.views.decorators import LOGIN_FORM_KEY
from django.http import HttpResponseRedirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from mezzanine.conf import settings


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
        is_login = LOGIN_FORM_KEY in request.POST
        is_logged_in = request.user.is_authenticated()
        site_selected = request.POST.get("interface") == "site"
        if is_login and not is_logged_in and site_selected:
            response = view_func(request, *view_args, **view_kwargs)
            if request.user.is_authenticated():
                return HttpResponseRedirect(request.GET.get("next", "/"))
            else:
                return response
        return None
