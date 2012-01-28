
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlquote

from mezzanine.conf import settings
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page
from mezzanine.utils.views import render


page_processors.autodiscover()


def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """
    get_id = lambda s: s.split("_")[-1]
    for ordering in ("ordering_from", "ordering_to"):
        ordering = request.POST.get(ordering, "")
        if ordering:
            for i, page in enumerate(ordering.split(",")):
                try:
                    Page.objects.filter(id=get_id(page)).update(_order=i)
                except Exception, e:
                    return HttpResponse(str(e))
    try:
        moved_page = int(get_id(request.POST.get("moved_page", "")))
    except ValueError, e:
        pass
    else:
        moved_parent = get_id(request.POST.get("moved_parent", ""))
        if not moved_parent:
            moved_parent = None
        try:
            page = Page.objects.get(id=moved_page)
            page.parent_id = moved_parent
            page.save()
            page.reset_slugs()
        except Exception, e:
            return HttpResponse(str(e))
    return HttpResponse("ok")
admin_page_ordering = staff_member_required(admin_page_ordering)


def page(request, slug, template="pages/page.html", extra_context=None):
    """
    Display content for a page. First check for any matching page processors
    and handle them. Secondly, build the list of template names to choose
    from given the slug and type of page being viewed.
    """
    page = get_object_or_404(Page.objects.published(request.user), slug=slug)
    if page.login_required and not request.user.is_authenticated():
        path = urlquote(request.get_full_path())
        url = "%s?%s=%s" % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
        return redirect(url)
    context = {"page": page}
    if extra_context is not None:
        context.update(extra_context)
    model_processors = page_processors.processors[page.content_model]
    slug_processors = page_processors.processors["slug:%s" % page.slug]
    for processor in model_processors + slug_processors:
        response = processor(request, page)
        if isinstance(response, HttpResponse):
            return response
        elif response:
            try:
                context.update(response)
            except (TypeError, ValueError):
                name = "%s.%s" % (processor.__module__, processor.__name__)
                error = ("The page processor %s returned %s but must return "
                         "HttpResponse or dict." % (name, type(response)))
                raise ValueError(error)
    templates = [u"pages/%s.html" % slug]
    if page.content_model is not None:
        templates.append(u"pages/%s.html" % page.content_model)
    templates.append(template)
    return render(request, templates, context)
