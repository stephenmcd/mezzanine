from __future__ import absolute_import, unicode_literals
from future.builtins import int, open, str

import os

from json import dumps
try:
    from urllib.parse import urljoin, urlparse
except ImportError:
    from urlparse import urljoin, urlparse

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.options import ModelAdmin
from django.contrib.staticfiles import finders
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseServerError,
                         HttpResponseNotFound)
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import requires_csrf_token

from mezzanine.conf import settings
from mezzanine.core.forms import get_edit_form
from mezzanine.core.models import Displayable, SitePermission
from mezzanine.utils.cache import add_cache_bypass
from mezzanine.utils.views import is_editable, paginate, render, set_cookie
from mezzanine.utils.sites import has_site_permission
from mezzanine.utils.urls import next_url


def set_device(request, device=""):
    """
    Sets a device name in a cookie when a user explicitly wants to go
    to the site for a particular device (eg mobile).
    """
    response = redirect(add_cache_bypass(next_url(request) or "/"))
    set_cookie(response, "mezzanine-device", device, 60 * 60 * 24 * 365)
    return response


@staff_member_required
def set_site(request):
    """
    Put the selected site ID into the session - posted to from
    the "Select site" drop-down in the header of the admin. The
    site ID is then used in favour of the current request's
    domain in ``mezzanine.core.managers.CurrentSiteManager``.
    """
    site_id = int(request.GET["site_id"])
    if not request.user.is_superuser:
        try:
            SitePermission.objects.get(user=request.user, sites=site_id)
        except SitePermission.DoesNotExist:
            raise PermissionDenied
    request.session["site_id"] = site_id
    admin_url = reverse("admin:index")
    next = next_url(request) or admin_url
    # Don't redirect to a change view for an object that won't exist
    # on the selected site - go to its list view instead.
    if next.startswith(admin_url):
        parts = next.split("/")
        if len(parts) > 4 and parts[4].isdigit():
            next = "/".join(parts[:4])
    return redirect(next)


def direct_to_template(request, template, extra_context=None, **kwargs):
    """
    Replacement for Django's ``direct_to_template`` that uses
    ``TemplateResponse`` via ``mezzanine.utils.views.render``.
    """
    context = extra_context or {}
    context["params"] = kwargs
    for (key, value) in context.items():
        if callable(value):
            context[key] = value()
    return render(request, template, context)


@staff_member_required
def edit(request):
    """
    Process the inline editing form.
    """
    model = apps.get_model(request.POST["app"], request.POST["model"])
    obj = model.objects.get(id=request.POST["id"])
    form = get_edit_form(obj, request.POST["fields"], data=request.POST,
                         files=request.FILES)
    if not (is_editable(obj, request) and has_site_permission(request.user)):
        response = _("Permission denied")
    elif form.is_valid():
        form.save()
        model_admin = ModelAdmin(model, admin.site)
        message = model_admin.construct_change_message(request, form, None)
        model_admin.log_change(request, obj, message)
        response = ""
    else:
        response = list(form.errors.values())[0][0]
    return HttpResponse(response)


def search(request, template="search_results.html", extra_context=None):
    """
    Display search results. Takes an optional "contenttype" GET parameter
    in the form "app-name.ModelName" to limit search results to a single model.
    """
    query = request.GET.get("q", "")
    page = request.GET.get("page", 1)
    per_page = settings.SEARCH_PER_PAGE
    max_paging_links = settings.MAX_PAGING_LINKS
    try:
        parts = request.GET.get("type", "").split(".", 1)
        search_model = apps.get_model(*parts)
        search_model.objects.search  # Attribute check
    except (ValueError, TypeError, LookupError, AttributeError):
        search_model = Displayable
        search_type = _("Everything")
    else:
        search_type = search_model._meta.verbose_name_plural.capitalize()
    results = search_model.objects.search(query, for_user=request.user)
    paginated = paginate(results, page, per_page, max_paging_links)
    context = {"query": query, "results": paginated,
               "search_type": search_type}
    context.update(extra_context or {})
    return render(request, template, context)


@staff_member_required
def static_proxy(request):
    """
    Serves TinyMCE plugins inside the inline popups and the uploadify
    SWF, as these are normally static files, and will break with
    cross-domain JavaScript errors if ``STATIC_URL`` is an external
    host. URL for the file is passed in via querystring in the inline
    popup plugin template, and we then attempt to pull out the relative
    path to the file, so that we can serve it locally via Django.
    """
    normalize = lambda u: ("//" + u.split("://")[-1]) if "://" in u else u
    url = normalize(request.GET["u"])
    host = "//" + request.get_host()
    static_url = normalize(settings.STATIC_URL)
    for prefix in (host, static_url, "/"):
        if url.startswith(prefix):
            url = url.replace(prefix, "", 1)
    response = ""
    content_type = ""
    path = finders.find(url)
    if path:
        if isinstance(path, (list, tuple)):
            path = path[0]
        if url.endswith(".htm"):
            # Inject <base href="{{ STATIC_URL }}"> into TinyMCE
            # plugins, since the path static files in these won't be
            # on the same domain.
            static_url = settings.STATIC_URL + os.path.split(url)[0] + "/"
            if not urlparse(static_url).scheme:
                static_url = urljoin(host, static_url)
            base_tag = "<base href='%s'>" % static_url
            content_type = "text/html"
            with open(path, "r") as f:
                response = f.read().replace("<head>", "<head>" + base_tag)
        else:
            content_type = "application/octet-stream"
            with open(path, "rb") as f:
                response = f.read()
    return HttpResponse(response, content_type=content_type)


def displayable_links_js(request):
    """
    Renders a list of url/title pairs for all ``Displayable`` subclass
    instances into JSON that's used to populate a list of links in
    TinyMCE.
    """
    links = []
    if "mezzanine.pages" in settings.INSTALLED_APPS:
        from mezzanine.pages.models import Page
        is_page = lambda obj: isinstance(obj, Page)
    else:
        is_page = lambda obj: False
    # For each item's title, we use its model's verbose_name, but in the
    # case of Page subclasses, we just use "Page", and then sort the items
    # by whether they're a Page subclass or not, then by their URL.
    for url, obj in Displayable.objects.url_map(for_user=request.user).items():
        title = getattr(obj, "titles", obj.title)
        real = hasattr(obj, "id")
        page = is_page(obj)
        if real:
            verbose_name = _("Page") if page else obj._meta.verbose_name
            title = "%s: %s" % (verbose_name, title)
        links.append((not page and real, {"title": str(title), "value": url}))
    return HttpResponse(dumps([link[1] for link in sorted(links)]))


@requires_csrf_token
def page_not_found(request, template_name="errors/404.html"):
    """
    Mimics Django's 404 handler but with a different template path.
    """
    context = RequestContext(request, {
        "STATIC_URL": settings.STATIC_URL,
        "request_path": request.path,
    })
    t = get_template(template_name)
    return HttpResponseNotFound(t.render(context))


@requires_csrf_token
def server_error(request, template_name="errors/500.html"):
    """
    Mimics Django's error handler but adds ``STATIC_URL`` to the
    context.
    """
    context = RequestContext(request, {"STATIC_URL": settings.STATIC_URL})
    t = get_template(template_name)
    return HttpResponseServerError(t.render(context))
