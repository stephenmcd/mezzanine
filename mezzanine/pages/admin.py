
from copy import deepcopy

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import NoReverseMatch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from mezzanine.pages.models import Page, RichTextPage
from mezzanine.core.admin import DisplayableAdmin
from mezzanine.utils.urls import admin_url


page_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
page_fieldsets[0][1]["fields"] += (("in_navigation", "in_footer"),
                                    "login_required",)


class PageAdmin(DisplayableAdmin):
    """
    Admin class for the ``Page`` model and all subclasses of
    ``Page``. Handles redirections between admin interfaces for the
    ``Page`` model and its subclasses.
    """

    fieldsets = page_fieldsets

    def in_menu(self):
        """
        Hide subclasses from the admin menu.
        """
        return self.model is Page

    def _check_permission(self, request, page, permission):
        """
        Runs the custom permission check and raises an
        exception if False.
        """
        if not getattr(page, "can_" + permission)(request):
            raise PermissionDenied

    def add_view(self, request, extra_context=None, **kwargs):
        """
        For the ``Page`` model, redirect to the add view for the
        ``RichText`` model.
        """
        if self.model is Page:
            try:
                add_url = admin_url(RichTextPage, "add")
                return HttpResponseRedirect(add_url)
            except NoReverseMatch:
                pass
        return super(PageAdmin, self).add_view(request, **kwargs)

    def change_view(self, request, object_id, extra_context=None):
        """
        For the ``Page`` model, check ``page.get_content_model()``
        for a subclass and redirect to its admin change view.
        Also enforce custom change permissions for the page instance.
        """
        page = get_object_or_404(Page, pk=object_id)
        content_model = page.get_content_model()
        self._check_permission(request, content_model, "change")
        if self.model is Page:
            if content_model is not None:
                change_url = admin_url(content_model.__class__, "change",
                                       content_model.id)
                return HttpResponseRedirect(change_url)
        extra_context = extra_context or {}
        extra_context["hide_delete_link"] = not page.can_delete(request)
        extra_context["hide_slug_field"] = page.overridden()
        return super(PageAdmin, self).change_view(request, object_id,
                                                  extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        """
        Enforce custom delete permissions for the page instance.
        """
        page = get_object_or_404(Page, pk=object_id)
        content_model = page.get_content_model()
        self._check_permission(request, content_model, "delete")
        return super(PageAdmin, self).delete_view(request, object_id,
                                                  extra_context)

    def changelist_view(self, request, extra_context=None):
        """
        Redirect to the ``Page`` changelist view for ``Page``
        subclasses.
        """
        if self.model is not Page:
            return HttpResponseRedirect(admin_url(Page, "changelist"))
        return super(PageAdmin, self).changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        """
        Set the ID of the parent page if passed in via querystring.
        """
        # Force parent to be saved to trigger handling of ordering and slugs.
        parent = request.GET.get("parent")
        if parent is not None and not change:
            obj.parent_id = parent
            obj._order = None
            obj.slug = None
            obj.save()
        super(PageAdmin, self).save_model(request, obj, form, change)

    def _maintain_parent(self, request, response):
        """
        Maintain the parent ID in the querystring for response_add and
        response_change.
        """
        location = response._headers.get("location")
        parent = request.GET.get("parent")
        if parent and location and "?" not in location[1]:
            url = "%s?parent=%s" % (location[1], parent)
            return HttpResponseRedirect(url)
        return response

    def response_add(self, request, obj):
        """
        Enforce page permissions and maintain the parent ID in the
        querystring.
        """
        response = super(PageAdmin, self).response_add(request, obj)
        return self._maintain_parent(request, response)

    def response_change(self, request, obj):
        """
        Enforce page permissions and maintain the parent ID in the
        querystring.
        """
        response = super(PageAdmin, self).response_change(request, obj)
        return self._maintain_parent(request, response)


richtext_fieldsets = deepcopy(PageAdmin.fieldsets)
richtext_fieldsets[0][1]["fields"].insert(3, "content")


class RichTextPageAdmin(PageAdmin):
    """
    Admin class for the ``RichText`` default content type.
    """
    fieldsets = richtext_fieldsets


admin.site.register(Page, PageAdmin)
admin.site.register(RichTextPage, RichTextPageAdmin)
