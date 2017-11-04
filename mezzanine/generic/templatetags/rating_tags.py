from __future__ import unicode_literals

from mezzanine import template
from mezzanine.generic.forms import RatingForm


register = template.Library()


@register.inclusion_tag("generic/includes/rating.html", takes_context=True)
def rating_for(context, obj):
    """
    Provides a generic context variable name for the object that
    ratings are being rendered for, and the rating form.
    """
    context["rating_object"] = context["rating_obj"] = obj
    context["rating_form"] = RatingForm(context["request"], obj)
    ratings = context["request"].COOKIES.get("mezzanine-rating", "")
    rating_string = "%s.%s" % (obj._meta, obj.pk)
    context["rated"] = (rating_string in ratings)
    rating_name = obj.get_ratingfield_name()
    for f in ("average", "count", "sum"):
        context["rating_" + f] = getattr(obj, "%s_%s" % (rating_name, f))
    return context.flatten()
