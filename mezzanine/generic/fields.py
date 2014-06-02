from __future__ import division, unicode_literals
from future.builtins import str

from copy import copy

from django.conf import settings
from django.contrib.contenttypes.generic import GenericRelation
from django.core.exceptions import ImproperlyConfigured
from django.db.models import IntegerField, CharField, FloatField
from django.db.models.signals import post_save, post_delete

from mezzanine.utils.models import lazy_model_ops


class BaseGenericRelation(GenericRelation):
    """
    Extends ``GenericRelation`` to:

    - Add a consistent default value for ``object_id_field`` and
      check for a ``related_model`` attribute which can be defined
      on subclasses as a default for the ``to`` argument.

    - Add one or more custom fields to the model that the relation
      field is applied to, and then call a ``related_items_changed``
      method each time related items are saved or deleted, so that a
      calculated value can be stored against the custom fields since
      aggregates aren't available for GenericRelation instances.

    """

    # Mapping of field names to model fields that will be added.
    fields = {}

    def __init__(self, *args, **kwargs):
        """
        Set up some defaults and check for a ``related_model``
        attribute for the ``to`` argument.
        """
        if kwargs.get("frozen_by_south", False):
            raise Exception("""

    Your project contains migrations that include one of the fields
    from mezzanine.generic in its Migration.model dict: possibly
    KeywordsField, CommentsField or RatingField. These migratons no
    longer work with the latest versions of Django and South, so you'll
    need to fix them by hand. This is as simple as commenting out or
    deleting the field from the Migration.model dict.
    See http://bit.ly/1hecVsD for an example.

    """)

        kwargs.setdefault("object_id_field", "object_pk")
        to = getattr(self, "related_model", None)
        if to:
            kwargs.setdefault("to", to)
        super(BaseGenericRelation, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        """
        Add each of the names and fields in the ``fields`` attribute
        to the model the relationship field is applied to, and set up
        the related item save and delete signals for calling
        ``related_items_changed``.
        """
        for field in cls._meta.many_to_many:
            if isinstance(field, self.__class__):
                e = "Multiple %s fields are not supported (%s.%s, %s.%s)" % (
                    self.__class__.__name__, cls.__name__, cls.__name__,
                    name, field.name)
                raise ImproperlyConfigured(e)
        self.related_field_name = name
        super(BaseGenericRelation, self).contribute_to_class(cls, name)
        # Not applicable to abstract classes, and in fact will break.
        if not cls._meta.abstract:
            for (name_string, field) in self.fields.items():
                if "%s" in name_string:
                    name_string = name_string % name
                # In Django 1.6, add_to_class will be called on a
                # parent model's field more than once, so
                # contribute_to_class needs to be idempotent. We
                # don't call get_all_field_names() which fill the app
                # cache get_fields_with_model() is safe.
                if name_string in [i.name for i, _ in
                                   cls._meta.get_fields_with_model()]:
                    continue
                if field.verbose_name is None:
                    field.verbose_name = self.verbose_name
                cls.add_to_class(name_string, copy(field))
            # Add a getter function to the model we can use to retrieve
            # the field/manager by name.
            getter_name = "get_%s_name" % self.__class__.__name__.lower()
            cls.add_to_class(getter_name, lambda self: name)

            def connect_save(sender):
                post_save.connect(self._related_items_changed, sender=sender)

            def connect_delete(sender):
                post_delete.connect(self._related_items_changed, sender=sender)

            lazy_model_ops.add(connect_save, self.rel.to)
            lazy_model_ops.add(connect_delete, self.rel.to)

    def _related_items_changed(self, **kwargs):
        """
        Ensure that the given related item is actually for the model
        this field applies to, and pass the instance to the real
        ``related_items_changed`` handler.
        """
        for_model = kwargs["instance"].content_type.model_class()
        if issubclass(for_model, self.model):
            instance_id = kwargs["instance"].object_pk
            try:
                instance = for_model.objects.get(id=instance_id)
            except self.model.DoesNotExist:
                # Instance itself was deleted - signals are irrelevant.
                return
            if hasattr(instance, "get_content_model"):
                instance = instance.get_content_model()
            related_manager = getattr(instance, self.related_field_name)
            self.related_items_changed(instance, related_manager)

    def related_items_changed(self, instance, related_manager):
        """
        Can be implemented by subclasses - called whenever the
        state of related items change, eg they're saved or deleted.
        The instance for this field and the related manager for the
        field are passed as arguments.
        """
        pass

    def value_from_object(self, obj):
        """
        Returns the value of this field in the given model instance.
        Needed for Django 1.7: https://code.djangoproject.com/ticket/22552
        """
        return getattr(obj, self.attname).all()


class CommentsField(BaseGenericRelation):
    """
    Stores the number of comments against the
    ``COMMENTS_FIELD_NAME_count`` field when a comment is saved or
    deleted.
    """

    related_model = "generic.ThreadedComment"
    fields = {"%s_count": IntegerField(editable=False, default=0)}

    def related_items_changed(self, instance, related_manager):
        """
        Stores the number of comments. A custom ``count_filter``
        queryset gets checked for, allowing managers to implement
        custom count logic.
        """
        try:
            count = related_manager.count_queryset()
        except AttributeError:
            count = related_manager.count()
        count_field_name = list(self.fields.keys())[0] % \
                           self.related_field_name
        setattr(instance, count_field_name, count)
        instance.save()


class KeywordsField(BaseGenericRelation):
    """
    Stores the keywords as a single string into the
    ``KEYWORDS_FIELD_NAME_string`` field for convenient access when
    searching.
    """

    related_model = "generic.AssignedKeyword"
    fields = {"%s_string": CharField(editable=False, blank=True,
                                     max_length=500)}

    def __init__(self, *args, **kwargs):
        """
        Mark the field as editable so that it can be specified in
        admin class fieldsets and pass validation, and also so that
        it shows up in the admin form.
        """
        super(KeywordsField, self).__init__(*args, **kwargs)
        self.editable = True

    def formfield(self, **kwargs):
        """
        Provide the custom form widget for the admin, since there
        isn't a form field mapped to ``GenericRelation`` model fields.
        """
        from mezzanine.generic.forms import KeywordsWidget
        kwargs["widget"] = KeywordsWidget
        return super(KeywordsField, self).formfield(**kwargs)

    def save_form_data(self, instance, data):
        """
        The ``KeywordsWidget`` field will return data as a string of
        comma separated IDs for the ``Keyword`` model - convert these
        into actual ``AssignedKeyword`` instances. Also delete
        ``Keyword`` instances if their last related ``AssignedKeyword``
        instance is being removed.
        """
        from mezzanine.generic.models import AssignedKeyword, Keyword
        related_manager = getattr(instance, self.name)
        # Get a list of Keyword IDs being removed.
        old_ids = [str(a.keyword_id) for a in related_manager.all()]
        new_ids = data.split(",")
        removed_ids = set(old_ids) - set(new_ids)
        # Remove current AssignedKeyword instances.
        related_manager.all().delete()
        # Convert the data into AssignedKeyword instances.
        if data:
            data = [AssignedKeyword(keyword_id=i) for i in new_ids]
        # Remove Keyword instances than no longer have a
        # related AssignedKeyword instance.
        existing = AssignedKeyword.objects.filter(keyword__id__in=removed_ids)
        existing_ids = set([str(a.keyword_id) for a in existing])
        unused_ids = removed_ids - existing_ids
        Keyword.objects.filter(id__in=unused_ids).delete()
        super(KeywordsField, self).save_form_data(instance, data)

    def contribute_to_class(self, cls, name):
        """
        Swap out any reference to ``KeywordsField`` with the
        ``KEYWORDS_FIELD_string`` field in ``search_fields``.
        """
        super(KeywordsField, self).contribute_to_class(cls, name)
        string_field_name = list(self.fields.keys())[0] % \
                            self.related_field_name
        if hasattr(cls, "search_fields") and name in cls.search_fields:
            try:
                weight = cls.search_fields[name]
            except TypeError:
                # search_fields is a sequence.
                index = cls.search_fields.index(name)
                search_fields_type = type(cls.search_fields)
                cls.search_fields = list(cls.search_fields)
                cls.search_fields[index] = string_field_name
                cls.search_fields = search_fields_type(cls.search_fields)
            else:
                del cls.search_fields[name]
                cls.search_fields[string_field_name] = weight

    def related_items_changed(self, instance, related_manager):
        """
        Stores the keywords as a single string for searching.
        """
        assigned = related_manager.select_related("keyword")
        keywords = " ".join([str(a.keyword) for a in assigned])
        string_field_name = list(self.fields.keys())[0] % \
                            self.related_field_name
        if getattr(instance, string_field_name) != keywords:
            setattr(instance, string_field_name, keywords)
            instance.save()


class RatingField(BaseGenericRelation):
    """
    Stores the rating count and average against the
    ``RATING_FIELD_NAME_count`` and ``RATING_FIELD_NAME_average``
    fields when a rating is saved or deleted.
    """

    related_model = "generic.Rating"
    fields = {"%s_count": IntegerField(default=0, editable=False),
              "%s_sum": IntegerField(default=0, editable=False),
              "%s_average": FloatField(default=0, editable=False)}

    def related_items_changed(self, instance, related_manager):
        """
        Calculates and saves the average rating.
        """
        ratings = [r.value for r in related_manager.all()]
        count = len(ratings)
        _sum = sum(ratings)
        average = _sum / count if count > 0 else 0
        setattr(instance, "%s_count" % self.related_field_name, count)
        setattr(instance, "%s_sum" % self.related_field_name, _sum)
        setattr(instance, "%s_average" % self.related_field_name, average)
        instance.save()


# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(rules=[((BaseGenericRelation,), [], {})],
            patterns=["mezzanine\.generic\.fields\."])
    except ImportError:
        pass
