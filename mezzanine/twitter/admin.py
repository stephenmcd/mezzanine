
from __future__ import unicode_literals

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import truncatechars

from mezzanine.twitter import get_auth_settings

try:
    from twitter import Api
except ImportError:
    Api = None


FORMFIELD_HTML = """
<div class='send_tweet_container'>
    <input id='id_send_tweet' name='send_tweet' type='checkbox'>
    <label class='vCheckboxLabel' for='id_send_tweet'>%s</label>
</div>
"""


class TweetableAdminMixin(object):
    """
    Admin mixin that adds a "Send to Twitter" checkbox to the add/change
    views, which when checked, will send a tweet with the title and link
    to the object being saved.
    """

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Adds the "Send to Twitter" checkbox after the "status" field,
        provided by any ``Displayable`` models. The approach here is
        quite a hack, however the sane approach of using a custom
        form with a boolean field defined, and then adding it to the
        formssets attribute of the admin class fell apart quite
        horrifically.
        """
        formfield = super(TweetableAdminMixin,
            self).formfield_for_dbfield(db_field, **kwargs)
        if Api and db_field.name == "status" and get_auth_settings():
            def wrapper(render):
                def wrapped(*args, **kwargs):
                    rendered = render(*args, **kwargs)
                    label = _("Send to Twitter")
                    return mark_safe(rendered + FORMFIELD_HTML % label)
                return wrapped
            formfield.widget.render = wrapper(formfield.widget.render)
        return formfield

    def save_model(self, request, obj, form, change):
        """
        Sends a tweet with the title/short_url if applicable.
        """
        super(TweetableAdminMixin, self).save_model(request, obj, form, change)
        if Api and request.POST.get("send_tweet", False):
            auth_settings = get_auth_settings()
            obj.set_short_url()
            message = truncatechars(obj, 140 - len(obj.short_url) - 1)
            api = Api(*auth_settings)
            api.PostUpdate("%s %s" % (message, obj.short_url))
