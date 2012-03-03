
import os

def host_theme_path(request):
    """
    Returns the directory of the theme associated with the given host
    """
    from mezzanine.conf import settings
    for (host, theme) in settings.HOST_THEMES:
        if host == request.get_host().split(":")[0]:
            try:
                return ("%s" % os.path.dirname(os.path.abspath(__import__(theme).__file__)))
            except ImportError:
                pass
    return ""

def templates_for_host(request, templates):
    """
    Given a template name (or list of them), returns the template names
    as a list, with each name prefixed with the device directory
    inserted into the front of the list.
    """
    from mezzanine.conf import settings
    if not isinstance(templates, (list, tuple)):
        templates = [templates]
    theme_dir = host_theme_path(request)
    host_templates = []
    if theme_dir:
        for template in templates:
            host_templates.append("%s/templates/%s" % (theme_dir, template))
    return host_templates + templates
