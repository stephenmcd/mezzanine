
from django.contrib.admin.views.decorators import LOGIN_FORM_KEY
from django.http import HttpResponseRedirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from mezzanine.settings import MOBILE_USER_AGENTS


class MobileTemplate(object):
    """
    If a mobile user agent is detected, inspect the default args for the view 
    func, and if a template name is found assume it is the template arg and 
    attempt to load a mobile template based on the original template name.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if [check for check in MOBILE_USER_AGENTS if check in user_agent]:
            template = view_kwargs.get("template")
            if template is None:
                for default in view_func.func_defaults:
                    if str(default).endswith(".html"):
                        template = default
            if template is not None:
                template = template.rsplit(".html", 1)[0] + ".mobile.html"
                try:
                    get_template(template)
                except TemplateDoesNotExist:
                    pass
                else:
                    view_kwargs["template"] = template
                    return view_func(request, *view_args, **view_kwargs)
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

