import inspect

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from mezzanine.settings import MOBILE_USER_AGENTS


def use_mobile_template(view_func):
    """
    If a mobile user agent is detected, inspect the default args for the view
    func, and if a template name is found then attempt to load a mobile
    template based on the original template name.
    """
    def view(request, *args, **kwargs):
        import pdb;pdb.set_trace()
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if [check for check in MOBILE_USER_AGENTS if check in user_agent]:
            template = kwargs.get("template")
            if template is None:
                args_, _, _, defaults = inspect.getargspec(view_func)
                if defaults:
                    arg_defaults = dict(zip(args_[-len(defaults):], defaults))
                    template = arg_defaults.get("template")
            if template is not None and template.endswith('.html'):
                mobile_template = template[:-4] + "mobile.html"
                try:
                    get_template(mobile_template)
                except TemplateDoesNotExist:
                    pass
                else:
                    kwargs["template"] = mobile_template
        return view_func(request, *args, **kwargs)
    return view
