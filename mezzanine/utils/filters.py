from urllib import urlencode
from urllib2 import Request, urlopen

import django
from django.utils.translation import ugettext as _
from django.forms import EmailField, URLField, Textarea 

import mezzanine
from mezzanine.conf import settings

class AkismetFilter(object):
    def is_spam(self, request, form, url):
        """
        Identifies form data as being spam, using the http://akismet.com
        service. The Akismet API key should be specified in the
        ``AKISMET_API_KEY`` setting.

        The name, email, url and comment fields are all guessed from the
        form fields:

        * name: First field labelled "Name", also taking i18n into account.
        * email: First ``EmailField`` field.
        * url: First ``URLField`` field.
        * comment: First field with a ``Textarea`` widget.

        If the actual comment can't be extracted, spam checking is passed.

        The referrer field expects a hidden form field to pass the referrer
        through, since the HTTP_REFERER will be the URL the form is posted
        from. The hidden referrer field is made available by default with
        the ``{% fields_for %}`` templatetag used for rendering form fields.
        """
        if not settings.AKISMET_API_KEY:
            return False
        protocol = "http" if not request.is_secure() else "https"
        host = protocol + "://" + request.get_host()
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META["REMOTE_ADDR"])
        data = {
            "blog": host,
            "user_ip": ip,
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "referrer": request.POST.get("referrer", ""),
            "permalink": host + url,
            "comment_type": "comment" if "comment" in request.POST else "form",
        }
        for name, field in form.fields.items():
            data_field = None
            if field.label and field.label.lower() in ("name", _("Name").lower()):
                data_field = "comment_author"
            elif isinstance(field, EmailField):
                data_field = "comment_author_email"
            elif isinstance(field, URLField):
                data_field = "comment_author_url"
            elif isinstance(field.widget, Textarea):
                data_field = "comment"
            if data_field and not data.get(data_field):
                data[data_field] = form.cleaned_data.get(name)
        if not data.get("comment"):
            return False
        api_url = ("http://%s.rest.akismet.com/1.1/comment-check" %
                   settings.AKISMET_API_KEY)
        versions = (django.get_version(), mezzanine.__version__)
        headers = {"User-Agent": "Django/%s | Mezzanine/%s" % versions}
        try:
            response = urlopen(Request(api_url, urlencode(data), headers)).read()
        except Exception:
            return False
        return response == "true"
