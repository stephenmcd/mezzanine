import base64
import hashlib
import hmac
import time

from django.utils import simplejson

from mezzanine import template


register = template.Library()


@register.simple_tag
def disqus_id_for(obj):
    """
    Returns a unique identifier for the object to be used in
    DISQUS JavaScript.
    """
    return "%s-%s" % (obj._meta.object_name, obj.id)


@register.inclusion_tag("generic/includes/disqus_sso.html", takes_context=True)
def disqus_sso_script(context):
    """
    Provides a generic context variable which adds single-sign-on
    support to DISQUS if ``COMMENTS_DISQUS_API_PUBLIC_KEY`` and
    ``COMMENTS_DISQUS_API_SECRET_KEY`` are specified.
    """
    settings = context["settings"]
    public_key = getattr(settings, "COMMENTS_DISQUS_API_PUBLIC_KEY", "")
    secret_key = getattr(settings, "COMMENTS_DISQUS_API_SECRET_KEY", "")
    user = context["request"].user
    if public_key and secret_key and user.is_authenticated():
        context["public_key"] = public_key
        context["sso_data"] = _get_disqus_sso(user, public_key, secret_key)
    return context


def _get_disqus_sso(user, public_key, secret_key):
    # Based on snippet provided on http://docs.disqus.com/developers/sso/

    # create a JSON packet of our data attributes
    data = simplejson.dumps({
        'id': '%s' % user.id,
        'username': user.username,
        'email': user.email,
    })
    # encode the data to base64
    message = base64.b64encode(data)
    # generate a timestamp for signing the message
    timestamp = int(time.time())
    # generate our hmac signature
    sig = hmac.HMAC(str(secret_key), '%s %s' % (message, timestamp),
                    hashlib.sha1).hexdigest()

    # Messages are of the form <message> <signature> <timestamp>
    return '%s %s %s' % (message, sig, timestamp)
