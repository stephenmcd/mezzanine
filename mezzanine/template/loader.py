"""
This module redefines the loader functions from  ``django.template.loader`` 
that deal with template loading, specifically ``get_template`` and 
``select_template``. They're reproduced here to pass in a ``context`` arg 
which is used to handle device specific template loading.
"""

from django.template import TemplateDoesNotExist
from django.template.loader import get_template as _get_template


def get_template(template_name, context):
    print template_name
    return _get_template(template_name)


def select_template(template_name_list, context):
    """
    Given a list of template names, returns the first that can be loaded.
    """
    for template_name in template_name_list:
        try:
            return get_template(template_name, context)
        except TemplateDoesNotExist:
            continue
    # If we get here, none of the templates could be loaded
    raise TemplateDoesNotExist(", ".join(template_name_list))
