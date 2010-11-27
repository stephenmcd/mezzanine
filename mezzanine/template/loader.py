"""
This module redefines the loader functions from  ``django.template.loader`` 
that deal with template loading, specifically ``get_template`` and 
``select_template``. They're reproduced here to pass in a ``context`` arg 
which is used to handle device specific template loading.
"""

from django.template import TemplateDoesNotExist
from django.template.loader import select_template as _select_template


def get_template(template_name, context_instance):
    """
    Create a list of template names, prefixed with the device specific 
    template directory names and ordered based on matching the user agent 
    string in the request context. Pass the list to Django's original 
    ``select_template``.
    """
    from mezzanine.conf import settings
    template_name_list = [template_name]
    if settings.DEFAULT_DEVICE:
        default = "%s/%s" % (settings.DEFAULT_DEVICE, template_name)
        template_name_list.insert(0, default)
    try:
        user_agent = context_instance["request"].META["HTTP_USER_AGENT"]
    except KeyError:
        pass
    else:
        for (device, ua_strings) in settings.DEVICE_USER_AGENTS:
            if device != settings.DEFAULT_DEVICE:
                for ua_string in ua_strings:
                    if ua_string in user_agent:
                        path = "%s/%s" % (device, template_name)
                        template_name_list.insert(0, path)
                        break
    return _select_template(template_name_list)


def select_template(template_name_list, context_instance):
    """
    Given a list of template names, returns the first that can be loaded.
    """
    for template_name in template_name_list:
        try:
            return get_template(template_name, context_instance)
        except TemplateDoesNotExist:
            continue
    # If we get here, none of the templates could be loaded
    raise TemplateDoesNotExist(", ".join(template_name_list))
