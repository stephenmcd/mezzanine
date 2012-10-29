
import re
import unicodedata

from django.core.urlresolvers import resolve, reverse, NoReverseMatch, \
    get_script_prefix
from django.shortcuts import redirect
from django.utils.encoding import smart_unicode

from mezzanine.conf import settings
from mezzanine.utils.importing import import_dotted_path


def admin_url(model, url, object_id=None):
    """
    Returns the URL for the given model and admin url name.
    """
    opts = model._meta
    url = "admin:%s_%s_%s" % (opts.app_label, opts.object_name.lower(), url)
    args = ()
    if object_id is not None:
        args = (object_id,)
    return reverse(url, args=args)


def home_slug():
    """
    Returns the slug arg defined for the ``home`` urlpattern, which
    is the definitive source of the ``url`` field defined for an
    editable homepage object.
    """
    prefix = get_script_prefix()
    slug = reverse("home")
    if slug.startswith(prefix):
        slug = '/' + slug[len(prefix):]
    try:
        return resolve(slug).kwargs["slug"]
    except KeyError:
        return slug


def slugify(s):
    """
    Loads the callable defined by the ``SLUGIFY`` setting, which defaults
    to the ``slugify_unicode`` function.
    """
    return import_dotted_path(settings.SLUGIFY)(s)


def slugify_unicode(s):
    """
    Replacement for Django's slugify which allows unicode chars in
    slugs, for URLs in Chinese, Russian, etc.
    Adopted from https://github.com/mozilla/unicode-slugify/
    """
    chars = []
    for char in unicode(smart_unicode(s)):
        cat = unicodedata.category(char)[0]
        if cat in "LN" or char in "-_~":
            chars.append(char)
        elif cat == "Z":
            chars.append(" ")
    return re.sub("[-\s]+", "-", "".join(chars).strip()).lower()


def login_redirect(request):
    """
    Returns the redirect response for login/signup. Favors:
    - next param
    - LOGIN_REDIRECT_URL setting
    - homepage
    """
    ignorable_nexts = ("",)
    if "mezzanine.accounts" in settings.INSTALLED_APPS:
        from mezzanine.accounts import urls
        ignorable_nexts += (urls.SIGNUP_URL, urls.LOGIN_URL, urls.LOGOUT_URL)
    next = request.REQUEST.get("next", "")
    if next in ignorable_nexts:
        try:
            next = reverse(settings.LOGIN_REDIRECT_URL)
        except NoReverseMatch:
            next = "/"
    return redirect(next)


def path_to_slug(path):
    """
    Removes everything from the given URL path, including
    ``PAGES_SLUG`` if it is set, returning a slug that would match a
    ``Page`` instance's slug.
    """
    from mezzanine.urls import PAGES_SLUG
    for prefix in (settings.SITE_PREFIX, PAGES_SLUG):
        path = path.strip("/").replace(prefix, "", 1)
    return path or "/"
