from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.utils.translation import ugettext as _
from mezzanine.blocks.models import Block, RichTextBlock
from mezzanine.blocks.forms import BlockForm, RichTextBlockForm

def edit(request, pk, modelform_class=BlockForm, permission_check=None, template_name='blocks/edit.html', success_url=None):
    """
    This view provides a simple editor implementation for flatblocks.

    There are two customization hooks. First of all you can specify your own
    ModelForm class by passing it to the view using the ``modelform_class``
    keyword-argument.

    The other entry point helps you check permissions: Pass a simple function
    via the ``permission_check`` keyword-argument in order to check
    permissions on the flatblock-level::

        def my_perm_check(request, block):
            return request.user.is_staff

        # ...

        urlpatterns('blocks.views',
            url('blocks/(?P<pk>\d+)/edit/$', 'edit',
                kwargs={'permission_check': my_perm_check}),
        )

    The contract here is pretty simple: If the function returns False, the
    view will return HttpResponseForbidden. Otherwise it will pass.  So if you
    want to do some fancy redirects if the permissions are wrong, return your
    own HttpResponse-object/-subclass.

    If everything is alright with the permissions, simply return True.
    """
    flatblock = get_object_or_404(Block, pk=pk)
    if permission_check is not None:
        permcheck_result = permission_check(request, flatblock)
        if permcheck_result is False:
            return HttpResponseForbidden(_('You are not allowed to edit this block'))
        if isinstance(permcheck_result, HttpResponse):
            return permcheck_result

    session_key = 'block.origin.%d' % (int(pk), )
    if request.method == 'POST':
        origin = request.session.get(session_key,
                request.META.get('HTTP_REFERER', '/'))
        form = modelform_class(request.POST, instance=flatblock)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.slug = flatblock.slug
            instance.save()
            del request.session[session_key]
            redirect_to = success_url and success_url or origin
            return HttpResponseRedirect(redirect_to)
    else:
        origin = request.META.get('HTTP_REFERER', '/')
        # Don't set origin to this view's url no matter what
        origin = origin == request.get_full_path() and request.session.get(session_key, '/') or origin
        form = modelform_class(instance=flatblock)
        request.session[session_key] = origin
    return render_to_response(template_name, {
        'form': form,
        'origin': origin,
        'flatblock': flatblock,
        }, context_instance=RequestContext(request))
