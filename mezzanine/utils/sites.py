
import os

from django.contrib.sites.models import Site

from mezzanine.conf import settings
from mezzanine.core.request import current_request


def current_site_id():
    """
    Responsible for determining the current ``Site`` instance to use
    when retrieving data for any ``SiteRelated`` models. If a request
    is available, and the site can be determined from it, we store the
    site against the request for subsequent retrievals. Otherwise the
    order of checks is as follows:

      - ``site_id`` in session. Used in the admin so that admin users
        can switch sites and stay on the same domain for the admin.
      - host for the current request matched to the domain of the site
        instance.
      - ``MEZZANINE_SITE_ID`` environment variable, so management
        commands or anything else outside of a request can specify a
        site.
      - ``SITE_ID`` setting.

    """
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
