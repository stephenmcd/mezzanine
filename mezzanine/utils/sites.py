
import os

from mezzanine.conf import settings


def host_theme_path(request):
    """
    Returns the directory of the theme associated with the given host.
    """
    for (host, theme) in settings.HOST_THEMES:
        if host.lower() == request.get_host().split(":")[0].lower():
            try:
                module = __import__(theme)
            except ImportError:
                pass
            else:
                return os.path.dirname(os.path.abspath(module.__file__))
    return ""


def templates_for_host(request, templates):
    """
    Given a template name (or list of them), returns the template names
    as a list, with each name prefixed with the device directory
    inserted into the front of the list.
    """
    if not isinstance(templates, (list, tuple)):
        templates = [templates]
    theme_dir = host_theme_path(request)
    host_templates = []
    if theme_dir:
        for template in templates:
            host_templates.append("%s/templates/%s" % (theme_dir, template))
            host_templates.append(template)
        return host_templates
    return templates
