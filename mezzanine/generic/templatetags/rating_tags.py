
from mezzanine import template
from mezzanine.generic.fields import RatingField
from mezzanine.generic.forms import RatingForm


register = template.Library()


@register.inclusion_tag("generic/includes/rating.html", takes_context=True)
def rating_for(context, obj):
    """
    Provides a generic context variable name for the object that
    ratings are being rendered for, and the rating form.
    """
    context["rating_obj"] = obj
    context["rating_form"] = RatingForm(obj)
    for field in obj._meta.many_to_many:
        if isinstance(field, RatingField):
            context["rating_average"] = getattr(obj, "%s_average" % field.name)
            context["rating_count"] = getattr(obj, "%s_count" % field.name)
            break
    return context
