from __future__ import unicode_literals

from copy import deepcopy

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import NoReverseMatch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin, DisplayableAdminForm
from mezzanine.pages.models import Page, RichTextPage, Link
from mezzanine.utils.urls import admin_url


# Add extra fields for pages to the Displayable fields.
# We only add the menu field if PAGE_MENU_TEMPLATES has values.
page_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
if settings.PAGE_MENU_TEMPLATES:
    page_fieldsets[0][1]["fields"] += ("in_menus",)
page_fieldsets[0][1]["fields"] += ("login_required",)


class PageAdminForm(DisplayableAdminForm):

    def clean_slug(self):
        """
        Save the old slug to be used later in PageAdmin.save_model()
        to make the slug change propagate down the page tree.
        """
        self.instance._old_slug = self.instance.slug
        return self.cleaned_data['slug']


class PageAdmin(DisplayableAdmin):
    """
    Admin class for the ``Page`` model and all subclasses of
    ``Page``. Handles redirections between admin interfaces for the
    ``Page`` model and its subclasses.
    """

    form = PageAdminForm
    fieldsets = page_fieldsets
    change_list_template = "admin/pages/page/change_list.html"

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
            exclude_fields = Page._meta.get_all_field_names() + ["page_ptr"]
            try:
                exclude_fields.extend(self.exclude)
            except (AttributeError, TypeError):
                pass
            try:
                exclude_fields.extend(self.form.Meta.exclude)
            except (AttributeError, TypeError):
                pass
            fields = self.model._meta.fields + self.model._meta.many_to_many
            for field in reversed(fields):
                if field.name not in exclude_fields and field.editable:
                    if not hasattr(field, "translated_field"):
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

    def add_view(self, request, **kwargs):
        """
        For the ``Page`` model, redirect to the add view for the
        first page model, based on the ``ADD_PAGE_ORDER`` setting.
        """
        if self.model is Page:
            return HttpResponseRedirect(self.get_content_models()[0].add_url)
        return super(PageAdmin, self).add_view(request, **kwargs)

    def change_view(self, request, object_id, **kwargs):
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
        kwargs.setdefault("extra_context", {})
        kwargs["extra_context"].update({
            "hide_delete_link": not content_model.can_delete(request),
            "hide_slug_field": content_model.overridden(),
        })
        return super(PageAdmin, self).change_view(request, object_id, **kwargs)

    def delete_view(self, request, object_id, **kwargs):
        """
        Enforce custom delete permissions for the page instance.
        """
        page = get_object_or_404(Page, pk=object_id)
        content_model = page.get_content_model()
        self._check_permission(request, content_model, "delete")
        return super(PageAdmin, self).delete_view(request, object_id, **kwargs)

    def changelist_view(self, request, extra_context=None):
        """
        Redirect to the ``Page`` changelist view for ``Page``
        subclasses.
        """
        if self.model is not Page:
            return HttpResponseRedirect(admin_url(Page, "changelist"))
        if not extra_context:
            extra_context = {}
        extra_context["page_models"] = self.get_content_models()
        return super(PageAdmin, self).changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        """
        Set the ID of the parent page if passed in via querystring, and
        make sure the new slug propagates to all descendant pages.
        """
        if change and obj._old_slug != obj.slug:
            # _old_slug was set in PageAdminForm.clean_slug().
            new_slug = obj.slug or obj.generate_unique_slug()
            obj.slug = obj._old_slug
            obj.set_slug(new_slug)

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

    @classmethod
    def get_content_models(cls):
        """
        Return all Page subclasses that are admin registered, ordered
        based on the ``ADD_PAGE_ORDER`` setting.
        """
        models = []
        for model in Page.get_content_models():
            try:
                admin_url(model, "add")
            except NoReverseMatch:
                continue
            else:
                setattr(model, "meta_verbose_name", model._meta.verbose_name)
                setattr(model, "add_url", admin_url(model, "add"))
                models.append(model)
        order = [name.lower() for name in settings.ADD_PAGE_ORDER]

        def sort_key(page):
            name = "%s.%s" % (page._meta.app_label, page._meta.object_name)
            unordered = len(order)
            try:
                return (order.index(name.lower()), "")
            except ValueError:
                return (unordered, page.meta_verbose_name)
        return sorted(models, key=sort_key)

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
