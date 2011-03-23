
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models import IntegerField, signals


class BaseGenericRelation(GenericRelation):
    """
    Extends ``GenericRelation`` to add a consistent default value 
    for ``object_id_field`` and check for a ``related_model`` 
    attribute which can be defined on subclasses as a default 
    for the ``to`` argument.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("object_id_field", "object_pk")
        to = getattr(self, "related_model", None)
        if to:
            kwargs.setdefault("to", to)
        super(BaseGenericRelation, self).__init__(*args, **kwargs)


class GenericRelationWithCount(BaseGenericRelation):
    """
    Generic relation field that stores the count of related items 
    against an instance, each time a related item is saved or deleted, 
    using a custom ``RELATION_count`` field.
    """

    def contribute_to_class(self, cls, name):
        """
        Create the ``RELATION_count`` field for storing the count of 
        related items, using the related field's name, and set up the 
        signals for save and delete which will update the count field.
        """
        super(GenericRelationWithCount, self).contribute_to_class(cls, name)
        self.related_field_name = name
        self.count_field_name = "%s_count" % name
        count_field = IntegerField(editable=False, default=0)
        cls.add_to_class(self.count_field_name, count_field)
        signals.post_save.connect(self.save_count, self.rel.to, True)
        signals.post_delete.connect(self.save_count, self.rel.to, True)

    def save_count(self, **kwargs):
        """
        Signal handler for save/delete of a related item that updates 
        the count field. A custom ``count_filter`` queryset gets checked 
        for, allowing managers to implement custom count logic.
        """
        instance = self.model.objects.get(id=kwargs["instance"].object_pk)
        related_field = getattr(instance, self.related_field_name)
        count = getattr(related_field, "count_queryset", related_field.count)()
        setattr(instance, self.count_field_name, count)
        instance.save()


class CommentsField(GenericRelationWithCount):
    related_model = "generic.ThreadedComment"
