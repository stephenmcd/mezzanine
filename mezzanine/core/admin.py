from __future__ import unicode_literals

from copy import deepcopy

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User as AuthUser
from django.contrib.redirects.admin import RedirectAdmin
from django.contrib.messages import error
from django.core.urlresolvers import NoReverseMatch
from django.forms import ValidationError, ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.forms import DynamicInlineAdminForm
from mezzanine.core.models import (
    Orderable, ContentTyped, SitePermission, CONTENT_STATUS_PUBLISHED)
from mezzanine.utils.models import base_concrete_model
from mezzanine.utils.sites import current_site_id
from mezzanine.utils.static import static_lazy as static
from mezzanine.utils.urls import admin_url

if settings.USE_MODELTRANSLATION:
    from collections import OrderedDict
    from django.utils.translation import activate, get_language
    from modeltranslation.admin import (TranslationAdmin,
                                        TranslationInlineModelAdmin)

    class BaseTranslationModelAdmin(TranslationAdmin):
        """
        Mimic modeltranslation's TabbedTranslationAdmin but uses a
        custom tabbed_translation_fields.js
        """
        class Media:
            js = (
                static("modeltranslation/js/force_jquery.js"),
                static("mezzanine/js/%s" % settings.JQUERY_UI_FILENAME),
                static("mezzanine/js/admin/tabbed_translation_fields.js"),
            )
            css = {
                "all": (static(
                    "mezzanine/css/admin/tabbed_translation_fields.css"),),
            }

else:
    class BaseTranslationModelAdmin(admin.ModelAdmin):
        """
        Abstract class used to handle the switch between translation
        and no-translation class logic. We define the basic structure
        for the Media class so we can extend it consistently regardless
        of whether or not modeltranslation is used.
        """
        class Media:
            js = ()
            css = {"all": ()}


User = get_user_model()


class DisplayableAdminForm(ModelForm):

    def clean_content(form):
        status = form.cleaned_data.get("status")
        content = form.cleaned_data.get("content")
        if status == CONTENT_STATUS_PUBLISHED and not content:
            raise ValidationError(_("This field is required if status "
                                    "is set to published."))
        return content


class DisplayableAdmin(BaseTranslationModelAdmin):
    """
    Admin class for subclasses of the abstract ``Displayable`` model.
    """

    list_display = ("title", "status", "admin_link")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status", "keywords__keyword")
    # modeltranslation breaks date hierarchy links, see:
    # https://github.com/deschler/django-modeltranslation/issues/324
    # Once that's resolved we can restore this.
    date_hierarchy = None if settings.USE_MODELTRANSLATION else "publish_date"
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {
            "fields": ["title", "status", ("publish_date", "expiry_date")],
        }),
        (_("Meta data"), {
            "fields": ["_meta_title", "slug",
                       ("description", "gen_description"),
                        "keywords", "in_sitemap"],
            "classes": ("collapse-closed",)
        }),
    )

    form = DisplayableAdminForm

    def __init__(self, *args, **kwargs):
        super(DisplayableAdmin, self).__init__(*args, **kwargs)
        try:
            self.search_fields = list(set(list(self.search_fields) + list(
                               self.model.objects.get_search_fields().keys())))
        except AttributeError:
            pass

    def check_permission(self, request, page, permission):
        """
        Subclasses can define a custom permission check and raise an exception
        if False.
        """
        pass

    def save_model(self, request, obj, form, change):
        """
        Save model for every language so that field auto-population
        is done for every each of it.
        """
        super(DisplayableAdmin, self).save_model(request, obj, form, change)
        if settings.USE_MODELTRANSLATION:
            lang = get_language()
            for code in OrderedDict(settings.LANGUAGES):
                if code != lang:  # Already done
                    try:
                        activate(code)
                    except:
                        pass
                    else:
                        obj.save()
            activate(lang)


class BaseDynamicInlineAdmin(object):
    """
    Admin inline that uses JS to inject an "Add another" link which
    when clicked, dynamically reveals another fieldset. Also handles
    adding the ``_order`` field and its widget for models that
    subclass ``Orderable``.
    """

    form = DynamicInlineAdminForm
    extra = 1

    def get_fields(self, request, obj=None):
        """
        For subclasses of ``Orderable``, the ``_order`` field must
        always be present and be the last field.
        """
        fields = super(BaseDynamicInlineAdmin, self).get_fields(request, obj)
        if issubclass(self.model, Orderable):
            fields = list(fields)
            try:
                fields.remove("_order")
            except ValueError:
                pass
            fields.append("_order")
        return fields

    def get_fieldsets(self, request, obj=None):
        """
        Same as above, but for fieldsets.
        """
        fieldsets = super(BaseDynamicInlineAdmin, self).get_fieldsets(
                                                            request, obj)
        if issubclass(self.model, Orderable):
            for fieldset in fieldsets:
                fields = [f for f in list(fieldset[1]["fields"])
                          if not hasattr(f, "translated_field")]
                try:
                    fields.remove("_order")
                except ValueError:
                    pass
                fieldset[1]["fields"] = fields
            fieldsets[-1][1]["fields"].append("_order")
        return fieldsets


def get_inline_base_class(cls):
    if settings.USE_MODELTRANSLATION:
        class InlineBase(TranslationInlineModelAdmin, cls):
            """
            Abstract class that mimics django-modeltranslation's
            Translation{Tabular,Stacked}Inline. Used as a placeholder
            for future improvement.
            """
            pass
        return InlineBase
    return cls


class TabularDynamicInlineAdmin(BaseDynamicInlineAdmin,
                                get_inline_base_class(admin.TabularInline)):
    pass


class StackedDynamicInlineAdmin(BaseDynamicInlineAdmin,
                                get_inline_base_class(admin.StackedInline)):

    def __init__(self, *args, **kwargs):
        """
        Stacked dynamic inlines won't work without grappelli
        installed, as the JavaScript in dynamic_inline.js isn't
        able to target each of the inlines to set the value of
        the order field.
        """
        grappelli_name = getattr(settings, "PACKAGE_NAME_GRAPPELLI")
        if grappelli_name not in settings.INSTALLED_APPS:
            error = "StackedDynamicInlineAdmin requires Grappelli installed."
            raise Exception(error)
        super(StackedDynamicInlineAdmin, self).__init__(*args, **kwargs)


class OwnableAdmin(admin.ModelAdmin):
    """
    Admin class for models that subclass the abstract ``Ownable``
    model. Handles limiting the change list to objects owned by the
    logged in user, as well as setting the owner of newly created
    objects to the logged in user.

    Remember that this will include the ``user`` field in the required
    fields for the admin change form which may not be desirable. The
    best approach to solve this is to define a ``fieldsets`` attribute
    that excludes the ``user`` field or simple add ``user`` to your
    admin excludes: ``exclude = ('user',)``
    """

    def save_form(self, request, form, change):
        """
        Set the object's owner as the logged in user.
        """
        obj = form.save(commit=False)
        if obj.user_id is None:
            obj.user = request.user
        return super(OwnableAdmin, self).save_form(request, form, change)

    def get_queryset(self, request):
        """
        Filter the change list by currently logged in user if not a
        superuser. We also skip filtering if the model for this admin
        class has been added to the sequence in the setting
        ``OWNABLE_MODELS_ALL_EDITABLE``, which contains models in the
        format ``app_label.object_name``, and allows models subclassing
        ``Ownable`` to be excluded from filtering, eg: ownership should
        not imply permission to edit.
        """
        opts = self.model._meta
        model_name = ("%s.%s" % (opts.app_label, opts.object_name)).lower()
        models_all_editable = settings.OWNABLE_MODELS_ALL_EDITABLE
        models_all_editable = [m.lower() for m in models_all_editable]
        qs = super(OwnableAdmin, self).get_queryset(request)
        if request.user.is_superuser or model_name in models_all_editable:
            return qs
        return qs.filter(user__id=request.user.id)


class ContentTypedAdmin(object):

    def __init__(self, *args, **kwargs):
        """
        For subclasses that are registered with an Admin class
        that doesn't implement fieldsets, add any extra model fields
        to this instance's fieldsets. This mimics Django's behaviour of
        adding all model fields when no fieldsets are defined on the
        Admin class.
        """
        super(ContentTypedAdmin, self).__init__(*args, **kwargs)

        self.concrete_model = base_concrete_model(ContentTyped, self.model)

        # Test that the fieldsets don't differ from the concrete admin's.
        if (self.model is not self.concrete_model and
                self.fieldsets == self.base_concrete_modeladmin.fieldsets):

            # Make a copy so that we aren't modifying other Admin
            # classes' fieldsets.
            self.fieldsets = deepcopy(self.fieldsets)

            # Insert each field between the publishing fields and nav
            # fields. Do so in reverse order to retain the order of
            # the model's fields.
            model_fields = self.concrete_model._meta.get_fields()
            concrete_field = '{concrete_model}_ptr'.format(
                concrete_model=self.concrete_model.get_content_model_name())
            exclude_fields = [f.name for f in model_fields] + [concrete_field]

            try:
                exclude_fields.extend(self.exclude)
            except (AttributeError, TypeError):
                pass

            try:
                exclude_fields.extend(self.form.Meta.exclude)
            except (AttributeError, TypeError):
                pass

            fields = (self.model._meta.get_fields() +
                      self.model._meta.many_to_many)
            for field in reversed(fields):
                if field.name not in exclude_fields and field.editable:
                    if not hasattr(field, "translated_field"):
                        self.fieldsets[0][1]["fields"].insert(3, field.name)

    @property
    def base_concrete_modeladmin(self):
        """ The class inheriting directly from ContentModelAdmin. """
        candidates = [self.__class__]
        while candidates:
            candidate = candidates.pop()
            if ContentTypedAdmin in candidate.__bases__:
                return candidate
            candidates.extend(candidate.__bases__)

        raise Exception("Can't find base concrete ModelAdmin class.")

    def has_module_permission(self, request):
        """
        Hide subclasses from the admin menu.
        """
        return self.model is self.concrete_model

    def change_view(self, request, object_id, **kwargs):
        """
        For the concrete model, check ``get_content_model()``
        for a subclass and redirect to its admin change view.
        """
        instance = get_object_or_404(self.concrete_model, pk=object_id)
        content_model = instance.get_content_model()

        self.check_permission(request, content_model, "change")

        if content_model.__class__ != self.model:
            change_url = admin_url(content_model.__class__, "change",
                                   content_model.id)
            return HttpResponseRedirect(change_url)

        return super(ContentTypedAdmin, self).change_view(
            request, object_id, **kwargs)

    def changelist_view(self, request, extra_context=None):
        """ Redirect to the changelist view for subclasses. """
        if self.model is not self.concrete_model:
            return HttpResponseRedirect(
                admin_url(self.concrete_model, "changelist"))

        extra_context = extra_context or {}
        extra_context["content_models"] = self.get_content_models()

        return super(ContentTypedAdmin, self).changelist_view(
            request, extra_context)

    def get_content_models(self):
        """ Return all subclasses that are admin registered. """
        models = []

        for model in self.concrete_model.get_content_models():
            try:
                admin_url(model, "add")
            except NoReverseMatch:
                continue
            else:
                setattr(model, "meta_verbose_name", model._meta.verbose_name)
                setattr(model, "add_url", admin_url(model, "add"))
                models.append(model)

        return models


####################################
# User Admin with Site Permissions #
####################################

class SitePermissionInline(admin.TabularInline):
    model = SitePermission
    max_num = 1
    can_delete = False


class SitePermissionUserAdmin(UserAdmin):

    inlines = [SitePermissionInline]

    def save_model(self, request, obj, form, change):
        """
        Provides a warning if the user is an active admin with no admin access.
        """
        super(SitePermissionUserAdmin, self).save_model(
            request, obj, form, change)
        user = self.model.objects.get(id=obj.id)
        has_perms = len(user.get_all_permissions()) > 0
        has_sites = SitePermission.objects.filter(user=user).count() > 0
        if user.is_active and user.is_staff and not user.is_superuser and not (
                has_perms and has_sites):
            error(request, "The user is active but won't be able to access "
                           "the admin, due to no edit/site permissions being "
                           "selected")


# only register if User hasn't been overridden
if User == AuthUser:
    if User in admin.site._registry:
        admin.site.unregister(User)
    admin.site.register(User, SitePermissionUserAdmin)


class SiteRedirectAdmin(RedirectAdmin):
    """
    Subclass of Django's redirect admin that modifies it to behave the
    way most other admin classes do it Mezzanine with regard to site
    filtering. It filters the list view by current site, hides the site
    field from the change form, and assigns the current site to the
    redirect when first created.
    """

    fields = ("old_path", "new_path")  # Excludes the site field.

    def get_queryset(self, request):
        """
        Filters the list view by current site.
        """
        queryset = super(SiteRedirectAdmin, self).get_queryset(request)
        return queryset.filter(site_id=current_site_id())

    def save_form(self, request, form, change):
        """
        Assigns the current site to the redirect when first created.
        """
        obj = form.save(commit=False)
        if not obj.site_id:
            obj.site_id = current_site_id()
        return super(SiteRedirectAdmin, self).save_form(request, form, change)


if "django.contrib.redirects" in settings.INSTALLED_APPS:
    from django.contrib.redirects.models import Redirect
    if Redirect in admin.site._registry:
        admin.site.unregister(Redirect)
    admin.site.register(Redirect, SiteRedirectAdmin)
