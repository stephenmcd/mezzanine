from django import template

register = template.Library()

# TODO: Remove this file a couple releases after Mezzanine 5
# We've kept this file because users upgrading to Mezzanine 5 might still refer to it.
# However, mezzanine.core.checks should warn them about it being deprecated.
