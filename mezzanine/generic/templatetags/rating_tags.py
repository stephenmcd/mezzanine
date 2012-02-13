
from django.template import Context
from django.template.loader import get_template

from mezzanine import template
from mezzanine.generic.forms import RatingForm


register = template.Library()


@register.render_tag
def rating_for(context, token):
    """
    Provides a generic context variable name for the object that
    ratings are being rendered for, and the rating form.
    """
    obj_name, field_name = token.split_contents()[1].split(".")
    obj = context[obj_name]
    initial = {"field_name": field_name}
    context["rating_average"] = getattr(obj, "%s_average" % field_name)
    context["object_for_rating"] = obj
    context["form_for_rating"] = RatingForm(obj, initial=initial)
    t = get_template("generic/includes/rating.html")
    return t.render(Context(context))
