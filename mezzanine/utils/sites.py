
import os

from django.contrib.sites.models import Site

from mezzanine.conf import settings
from mezzanine.core.request import current_request


def current_site_id():
    request = current_request()
    site_id = getattr(request, "site_id", None)
    if request and not site_id:
        site_id = request.session.get("site_id", None)
        if not site_id:
            domain = request.get_host().lower()
            try:
                site = Site.objects.get(domain__iexact=domain)
            except Site.DoesNotExist:
                pass
            else:
                site_id = site.id
        if request and site_id:
            request.site_id = site_id
    if not site_id:
        site_id = os.environ.get("MEZZANINE_SITE_ID", settings.SITE_ID)
    return site_id


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
