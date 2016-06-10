"""
Mixin classes for models that can be subclassed to create custom types.
In order to use them:

- Inherit model from CustomContentTypes.
- Inherit that model's ModelAdmin from CustomContentTypesAdmin.
- Include "content_typed/change_list.html" in the change_list.html template.
"""
from copy import deepcopy

from django.apps import apps
from django.core.urlresolvers import NoReverseMatch
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from mezzanine.utils.models import base_concrete_model
from mezzanine.utils.urls import admin_url


class ContentTyped(models.Model):
    content_model = models.CharField(editable=False, max_length=50, null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_content_model_name(cls):
        return cls._meta.object_name.lower()

    @classmethod
    def get_content_models(cls):
        """ Return all subclasses of the concrete model.  """
        concrete_model = base_concrete_model(ContentTyped, cls)
        return [m for m in apps.get_models()
                if m is not concrete_model and issubclass(m, concrete_model)]

    def get_content_model(self):
        return getattr(self, self.content_model, None)


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

            fields = self.model._meta.fields + self.model._meta.many_to_many
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

        if self.model is self.concrete_model:
            if content_model is not None:
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
