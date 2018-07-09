from __future__ import absolute_import, unicode_literals
from future.builtins import chr, int, str

try:
    from html.parser import HTMLParser
    from html.entities import name2codepoint
    try:
        from html.parser import HTMLParseError
    except ImportError:  # Python 3.5+
        class HTMLParseError(Exception):
            pass
except ImportError:  # Python 2
    from HTMLParser import HTMLParser, HTMLParseError
    from htmlentitydefs import name2codepoint

import re

from mezzanine.utils.deprecation import mark_safe


SELF_CLOSING_TAGS = ['br', 'img']
NON_SELF_CLOSING_TAGS = ['script', 'iframe']
ABSOLUTE_URL_TAGS = {"img": "src", "a": "href", "iframe": "src"}

# Tags and attributes added to richtext filtering whitelist when the
# RICHTEXT_FILTER_LEVEL is set to low. General use-case for these is
# allowing embedded video, but we will add to this fixed list over
# time as more use-cases come up. We won't ever add script tags or
# events (onclick etc) to this list. To enable those, filtering can
# be turned off in the settings admin.
LOW_FILTER_TAGS = ("iframe", "embed", "video", "param", "source", "object")
LOW_FILTER_ATTRS = ("allowfullscreen", "autostart", "loop", "hidden",
                    "playcount", "volume", "controls", "data", "classid")


def absolute_urls(html):
    """
    Converts relative URLs into absolute URLs. Used for RSS feeds to
    provide more complete HTML for item descriptions, but could also
    be used as a general richtext filter.
    """

    from bs4 import BeautifulSoup
    from mezzanine.core.request import current_request

    request = current_request()
    if request is not None:
        dom = BeautifulSoup(html, "html.parser")
        for tag, attr in ABSOLUTE_URL_TAGS.items():
            for node in dom.findAll(tag):
                url = node.get(attr, "")
                if url:
                    node[attr] = request.build_absolute_uri(url)
        html = str(dom)
    return html


def decode_entities(html):
    """
    Remove HTML entities from a string.
    Adapted from http://effbot.org/zone/re-sub.htm#unescape-html
    """
    def decode(m):
        html = m.group(0)
        if html[:2] == "&#":
            try:
                if html[:3] == "&#x":
                    return chr(int(html[3:-1], 16))
                else:
                    return chr(int(html[2:-1]))
            except ValueError:
                pass
        else:
            try:
                html = chr(name2codepoint[html[1:-1]])
            except KeyError:
                pass
        return html
    return re.sub("&#?\w+;", decode, html.replace("&amp;", "&"))


@mark_safe
def escape(html):
    """
    Escapes HTML according to the rules defined by the settings
    ``RICHTEXT_FILTER_LEVEL``, ``RICHTEXT_ALLOWED_TAGS``,
    ``RICHTEXT_ALLOWED_ATTRIBUTES``, ``RICHTEXT_ALLOWED_STYLES``.
    """
    from bleach import clean, ALLOWED_PROTOCOLS
    from mezzanine.conf import settings
    from mezzanine.core import defaults
    if settings.RICHTEXT_FILTER_LEVEL == defaults.RICHTEXT_FILTER_LEVEL_NONE:
        return html
    tags = settings.RICHTEXT_ALLOWED_TAGS
    attrs = settings.RICHTEXT_ALLOWED_ATTRIBUTES
    styles = settings.RICHTEXT_ALLOWED_STYLES
    if settings.RICHTEXT_FILTER_LEVEL == defaults.RICHTEXT_FILTER_LEVEL_LOW:
        tags += LOW_FILTER_TAGS
        attrs += LOW_FILTER_ATTRS
    if isinstance(attrs, tuple):
        attrs = list(attrs)
    return clean(html, tags=tags, attributes=attrs, strip=True,
                 strip_comments=False, styles=styles,
                 protocols=ALLOWED_PROTOCOLS + ["tel"])


@mark_safe
def thumbnails(html):
    """
    Given a HTML string, converts paths in img tags to thumbnail
    paths, using Mezzanine's ``thumbnail`` template tag. Used as
    one of the default values in the ``RICHTEXT_FILTERS`` setting.
    """
    from django.conf import settings
    from bs4 import BeautifulSoup
    from mezzanine.core.templatetags.mezzanine_tags import thumbnail

    # If MEDIA_URL isn't in the HTML string, there aren't any
    # images to replace, so bail early.
    if settings.MEDIA_URL.lower() not in html.lower():
        return html

    dom = BeautifulSoup(html, "html.parser")
    for img in dom.findAll("img"):
        src = img.get("src", "")
        src_in_media = src.lower().startswith(settings.MEDIA_URL.lower())
        width = img.get("width")
        height = img.get("height")
        if src_in_media and str(width).isdigit() and str(height).isdigit():
            img["src"] = settings.MEDIA_URL + thumbnail(src, width, height)
    # BS adds closing br tags, which the browser interprets as br tags.
    return str(dom).replace("</br>", "")


class TagCloser(HTMLParser):
    """
    HTMLParser that closes open tags. Takes a HTML string as its first
    arg, and populate a ``html`` attribute on the parser with the
    original HTML arg and any required closing tags.
    """

    def __init__(self, html):
        HTMLParser.__init__(self)
        self.html = html
        self.tags = []
        try:
            self.feed(self.html)
        except HTMLParseError:
            pass
        else:
            self.html += "".join(["</%s>" % tag for tag in self.tags])

    def handle_starttag(self, tag, attrs):
        if tag not in SELF_CLOSING_TAGS:
            self.tags.insert(0, tag)

    def handle_endtag(self, tag):
        try:
            self.tags.remove(tag)
        except ValueError:
            pass
