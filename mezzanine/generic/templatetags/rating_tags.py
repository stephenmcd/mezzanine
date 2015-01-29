from __future__ import unicode_literals

from mezzanine import template
from mezzanine.generic.forms import RatingForm
from mezzanine.generic.models import Rating


register = template.Library()


@register.inclusion_tag("generic/includes/rating.html", takes_context=True)
def rating_for(context, obj):
    """
    Provides a generic context variable name for the object that
    ratings are being rendered for, and the rating form.
    """
    context["rating_object"] = context["rating_obj"] = obj
    context["rating_form"] = RatingForm(context["request"], obj)
    rating_name = obj.get_ratingfield_name()
    rating_handle = getattr(obj,rating_name)
    try:
        context["rated"] = rating_handle.get(user=context["request"].user)
    except Rating.DoesNotExist:
        context["rated"] = False
    for f in ("average", "count", "sum"):
        context["rating_" + f] = getattr(obj, "%s_%s" % (rating_name, f))
    return context
