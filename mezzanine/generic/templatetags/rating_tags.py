
from mezzanine import template
from mezzanine.generic.forms import RatingForm


register = template.Library()


@register.inclusion_tag("generic/includes/rating.html", takes_context=True)
def rating_for(context, obj):
    """
    Provides a generic context variable name for the object that
    ratings are being rendered for, and the rating form.
    """
    context["object_for_rating"] = obj
    context["form_for_rating"] = RatingForm(obj)
    return context
