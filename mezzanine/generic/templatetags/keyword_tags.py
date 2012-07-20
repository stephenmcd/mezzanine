
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Count

from mezzanine import template
from mezzanine.conf import settings
from mezzanine.generic.fields import KeywordsField
from mezzanine.generic.models import AssignedKeyword, Keyword


register = template.Library()


@register.as_tag
def keywords_for(*args):
    """
    Return a list of ``Keyword`` objects for the given model instance
    or a model class. In the case of a model class, retrieve all
    keywords for all instances of the model and apply a ``weight``
    attribute that can be used to create a tag cloud.
    """

    # Handle a model instance.
    if isinstance(args[0], Model):
        obj = args[0]
        if hasattr(obj, "get_content_model"):
            obj = obj.get_content_model() or obj
        # There can only be one ``KeywordsField``, find it.
        for field in obj._meta.many_to_many:
            if isinstance(field, KeywordsField):
                break
        else:
            return []
        keywords_manager = getattr(obj, field.name)
        return [a.keyword for a in keywords_manager.select_related("keyword")]

    # Handle a model class.
    try:
        app_label, model = args[0].split(".", 1)
    except ValueError:
        return []

    content_type = ContentType.objects.get(app_label=app_label, model=model)
    assigned = AssignedKeyword.objects.filter(content_type=content_type)
    keywords = Keyword.objects.filter(assignments__in=assigned)
    keywords = keywords.annotate(item_count=Count("assignments"))
    if not keywords:
        return []
    settings.use_editable()
    counts = [keyword.item_count for keyword in keywords]
    min_count, max_count = min(counts), max(counts)
    sizes = settings.TAG_CLOUD_SIZES
    step = (max_count - min_count) / (sizes - 1)
    if step == 0:
        steps = [sizes / 2]
    else:
        steps = range(min_count, max_count, step)[:sizes]
    for keyword in keywords:
        c = keyword.item_count
        diff = min([(abs(s - c), (s - c)) for s in steps])[1]
        keyword.weight = steps.index(c + diff) + 1
    return keywords
