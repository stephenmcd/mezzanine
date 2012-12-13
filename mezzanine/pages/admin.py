
from copy import deepcopy

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import NoReverseMatch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from mezzanine.pages.models import Page, RichTextPage, Link
from mezzanine.core.admin import DisplayableAdmin
from mezzanine.utils.urls import admin_url


page_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
page_fieldsets[0][1]["fields"] += ("in_menus", "login_required",)


class PageAdmin(DisplayableAdmin):
    """
    Admin class for the ``Page`` model and all subclasses of
    ``Page``. Handles redirections between admin interfaces for the
    ``Page`` model and its subclasses.
    """

    fieldsets = page_fieldsets

    def __init__(self, *args, **kwargs):
        """
        For ``Page`` subclasses that are registered with an Admin class
        that doesn't implement fieldsets, add any extra model fields
        to this instance's fieldsets. This mimics Django's behaviour of
        adding all model fields when no fieldsets are defined on the
        Admin class.
        """
        super(PageAdmin, self).__init__(*args, **kwargs)
        # Test that the fieldsets don't differ from PageAdmin's.
        if self.model is not Page and self.fieldsets == PageAdmin.fieldsets:
            # Make a copy so that we aren't modifying other Admin
            # classes' fieldsets.
            self.fieldsets = deepcopy(self.fieldsets)
            # Insert each field between the publishing fields and nav
            # fields. Do so in reverse order to retain the order of
            # the model's fields.
            for field in reversed(self.model._meta.fields):
                check_fields = [f.name for f in Page._meta.fields]
                check_fields.append("page_ptr")
                try:
                    check_fields.extend(self.exclude)
                except (AttributeError, TypeError):
                    pass
                try:
                    check_fields.extend(self.form.Meta.exclude)
                except (AttributeError, TypeError):
                    pass
                if field.name not in check_fields and field.editable:
                    self.fieldsets[0][1]["fields"].insert(3, field.name)

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
                                                  extra_context=extra_context)

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


# Drop the meta data fields, and move slug towards the stop.
link_fieldsets = deepcopy(page_fieldsets[:1])
link_fieldsets[0][1]["fields"] = link_fieldsets[0][1]["fields"][:-1]
link_fieldsets[0][1]["fields"].insert(1, "slug")


class LinkAdmin(PageAdmin):

    fieldsets = link_fieldsets

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Make slug mandatory.
        """
        if db_field.name == "slug":
            kwargs["required"] = True
        return super(LinkAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def save_form(self, request, form, change):
        """
        Don't show links in the sitemap.
        """
        obj = form.save(commit=False)
        if not obj.id and "in_sitemap" not in form.fields:
            obj.in_sitemap = False
        return super(LinkAdmin, self).save_form(request, form, change)


admin.site.register(Page, PageAdmin)
admin.site.register(RichTextPage, PageAdmin)
admin.site.register(Link, LinkAdmin)
