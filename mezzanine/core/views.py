
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth import logout as auth_logout
from django.contrib.messages import info
from django.db.models import get_model
from django import http
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.forms import LoginForm, SignupForm, get_edit_form
from mezzanine.core.models import Displayable
from mezzanine.utils.views import is_editable, paginate, render
from mezzanine.utils.views import set_cookie


def account(request, template="account.html"):
    """
    Display and handle both the login and signup forms.
    """
    login_form = LoginForm()
    signup_form = SignupForm()
    if request.method == "POST":
        posted_form = None
        message = ""
        if request.POST.get("login") is not None:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                posted_form = login_form
                message = _("Successfully logged in")
        else:
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                signup_form.save()
                posted_form = signup_form
                message = _("Successfully signed up")
        if posted_form is not None:
            posted_form.login(request)
            info(request, message)
            return redirect(request.GET.get("next", "/"))
    context = {"login_form": login_form, "signup_form": signup_form}
    return render(request, template, context)


def logout(request):
    """
    Log the user out.
    """
    auth_logout(request)
    info(request, _("Successfully logged out"))
    return redirect(request.GET.get("next", "/"))


def set_device(request, device=""):
    """
    Sets a device name in a cookie when a user explicitly wants to go
    to the site for a particular device (eg mobile).
    """
    response = redirect(request.GET.get("next", "/"))
    set_cookie(response, "mezzanine-device", device, 60 * 60 * 24 * 365)
    return response


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


def edit(request):
    """
    Process the inline editing form.
    """
    model = get_model(request.POST["app"], request.POST["model"])
    obj = model.objects.get(id=request.POST["id"])
    form = get_edit_form(obj, request.POST["fields"], data=request.POST,
                         files=request.FILES)
    if not is_editable(obj, request):
        response = _("Permission denied")
    elif form.is_valid():
        form.save()
        model_admin = ModelAdmin(model, admin.site)
        message = model_admin.construct_change_message(request, form, None)
        model_admin.log_change(request, obj, message)
        response = ""
    else:
        response = form.errors.values()[0][0]
    return http.HttpResponse(unicode(response))


def search(request, template="search_results.html"):
    """
    Display search results.
    """
    settings.use_editable()
    query = request.GET.get("q", "")
    results = Displayable.objects.search(query)
    results = paginate(results, request.GET.get("page", 1),
                       settings.SEARCH_PER_PAGE,
                       settings.MAX_PAGING_LINKS)
    context = {"query": query, "results": results}
    return render(request, template, context)


def server_error(request, template_name='500.html'):
    """
    Mimics Django's error handler but adds ``STATIC_URL`` to the
    context.
    """
    context = RequestContext(request, {"STATIC_URL": settings.STATIC_URL})
    t = get_template(template_name)
    return http.HttpResponseServerError(t.render(context))
