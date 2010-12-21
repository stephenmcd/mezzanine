"""
This module redefines the loader functions from  ``django.template.loader``
that deal with template loading, specifically ``get_template`` and
``select_template``. They're reproduced here to pass in a ``context`` arg
which is used to handle device specific template loading.
"""

from django.template import TemplateDoesNotExist
from django.template.loader import select_template as _select_template

from mezzanine.utils.device import device_from_request


def get_template(template_name, context_instance):
    """
    Create a list of template paths for the given template name,
    prefixed with the device determined from the request, a default device 
    if set, and finally the original template name, all in this order.
    """
    from mezzanine.conf import settings
    template_name_list = []
    try:
        device = device_from_request(context_instance["request"])
    except KeyError:
        pass
    else:
        if device:
            template_name_list.append("%s/%s" % (device, template_name))
    if settings.DEFAULT_DEVICE:
        default = "%s/%s" % (settings.DEFAULT_DEVICE, template_name)
        if default not in template_name_list:
            template_name_list.append(default)
    template_name_list.append(template_name)
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
