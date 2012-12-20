
from copy import copy

from django.conf import settings
from django.contrib.contenttypes.generic import GenericRelation
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model, IntegerField, CharField, FloatField
from django.db.models.signals import post_save, post_delete


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
        self.frozen_by_south = kwargs.pop("frozen_by_south", False)
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
        if not cls._meta.abstract and not self.frozen_by_south:
            for (name_string, field) in self.fields.items():
                if "%s" in name_string:
                    name_string = name_string % name
                if not field.verbose_name:
                    field.verbose_name = self.verbose_name
                cls.add_to_class(name_string, copy(field))
            # For some unknown reason the signal won't be triggered
            # if given a sender arg, particularly when running
            # Cartridge with the field RichTextPage.keywords - so
            # instead of specifying self.rel.to as the sender, we
            # check for it inside the signal itself.
            post_save.connect(self._related_items_changed)
            post_delete.connect(self._related_items_changed)

    def _related_items_changed(self, **kwargs):
        """
        Ensure that the given related item is actually for the model
        this field applies to, and pass the instance to the real
        ``related_items_changed`` handler.
        """
        # Manually check that the instance matches the relation,
        # since we don't specify a sender for the signal.
        try:
            to = self.rel.to
            if isinstance(to, basestring):
                to = get_model(*to.split(".", 1))
            assert isinstance(kwargs["instance"], to)
        except (TypeError, ValueError, AssertionError):
            return
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
        count_field_name = self.fields.keys()[0] % self.related_field_name
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
        string_field_name = self.fields.keys()[0] % self.related_field_name
        if hasattr(cls, "search_fields") and name in cls.search_fields:
            try:
                weight = cls.search_fields[name]
            except AttributeError:
                # search_fields is a sequence.
                index = cls.search_fields.index(name)
                cls.search_fields[index] = string_field_name
            else:
                del cls.search_fields[name]
                cls.search_fields[string_field_name] = weight

    def related_items_changed(self, instance, related_manager):
        """
        Stores the keywords as a single string for searching.
        """
        assigned = related_manager.select_related("keyword")
        keywords = " ".join([unicode(a.keyword) for a in assigned])
        string_field_name = self.fields.keys()[0] % self.related_field_name
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
              "%s_average": FloatField(default=0, editable=False)}

    def related_items_changed(self, instance, related_manager):
        """
        Calculates and saves the average rating.
        """
        ratings = [r.value for r in related_manager.all()]
        count = len(ratings)
        average = sum(ratings) / float(count) if count > 0 else 0
        setattr(instance, "%s_count" % self.related_field_name, count)
        setattr(instance, "%s_average" % self.related_field_name, average)
        instance.save()


# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(rules=[((BaseGenericRelation,), [],
                            {"frozen_by_south": [True, {"is_value": True}]})],
            patterns=["mezzanine\.generic\.fields\."])
    except ImportError:
        pass
