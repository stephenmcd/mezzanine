from __future__ import unicode_literals
from future.builtins import int, round

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Count

from mezzanine import template
from mezzanine.conf import settings
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
        keywords_name = obj.get_keywordsfield_name()
        keywords_queryset = getattr(obj, keywords_name).all()
        # Keywords may have been prefetched already. If not, we
        # need select_related for the actual keywords.
        prefetched = getattr(obj, "_prefetched_objects_cache", {})
        if keywords_name not in prefetched:
            keywords_queryset = keywords_queryset.select_related("keyword")
        return [assigned.keyword for assigned in keywords_queryset]

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
    factor = (settings.TAG_CLOUD_SIZES - 1.)
    if min_count != max_count:
        factor /= (max_count - min_count)
    for kywd in keywords:
        kywd.weight = int(round((kywd.item_count - min_count) * factor)) + 1
    return keywords
