from __future__ import print_function
from __future__ import unicode_literals
from future.builtins import int

from datetime import datetime
from json import loads
from time import sleep

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from django.core.management.base import CommandError
from django.utils.html import strip_tags

from mezzanine.blog.management.base import BaseImporterCommand


MAX_POSTS_PER_CALL = 20  # Max number of posts Tumblr API will return per call.
MAX_RETRIES_PER_CALL = 3  # Max times to retry API call after failing.
SLEEP_PER_RETRY = 3  # Seconds to pause for between retries.


def title_from_content(content):
    """
    Try and extract the first sentence from a block of test to use as a title.
    """
    for end in (". ", "?", "!", "<br />", "\n", "</p>"):
        if end in content:
            content = content.split(end)[0] + end
            break
    return strip_tags(content)


class Command(BaseImporterCommand):
    """
    Import Tumblr blog posts into the blog app.
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "-t", "--tumblr-user", dest="tumblr_user",
            help="Tumblr username")

    help = "Import Tumblr blog posts into the blog app."

    def handle_import(self, options):

        tumblr_user = options.get("tumblr_user")
        if tumblr_user is None:
            raise CommandError("Usage is import_tumblr %s" % self.args)
        verbosity = int(options.get("verbosity", 1))
        json_url = "http://%s.tumblr.com/api/read/json" % tumblr_user
        json_start = "var tumblr_api_read ="
        date_format = "%a, %d %b %Y %H:%M:%S"
        start_index = 0

        while True:
            retries = MAX_RETRIES_PER_CALL
            try:
                call_url = "%s?start=%s" % (json_url, start_index)
                if verbosity >= 2:
                    print("Calling %s" % call_url)
                response = urlopen(call_url)
                if response.code == 404:
                    raise CommandError("Invalid Tumblr user.")
                elif response.code == 503:
                    # The Tumblr API is frequently unavailable so make a
                    # few tries, pausing between each.
                    retries -= 1
                    if not retries:
                        error = "Tumblr API unavailable, try again shortly."
                        raise CommandError(error)
                    sleep(3)
                    continue
                elif response.code != 200:
                    raise IOError("HTTP status %s" % response.code)
            except IOError as e:
                error = "Error communicating with Tumblr API (%s)" % e
                raise CommandError(error)

            data = response.read()
            json = loads(data.split(json_start, 1)[1].strip().rstrip(";"))
            posts = json["posts"]
            start_index += MAX_POSTS_PER_CALL

            for post in posts:
                handler = getattr(self, "handle_%s_post" % post["type"])
                if handler is not None:
                    title, content = handler(post)
                    pub_date = datetime.strptime(post["date"], date_format)
                    self.add_post(title=title, content=content,
                                  pub_date=pub_date, tags=post.get("tags"),
                                  old_url=post["url-with-slug"])
            if len(posts) < MAX_POSTS_PER_CALL:
                break

    def handle_regular_post(self, post):
        return post["regular-title"], post["regular-body"]

    def handle_link_post(self, post):
        title = post["link-text"]
        content = ('<p><a href="%(link-url)s">%(link-text)s</a></p>'
                  '%(link-description)s') % post
        return title, content

    def handle_quote_post(self, post):
        title = post["quote-text"]
        content = ("<blockquote>%(quote-text)s</blockquote>"
                  "<p>%(quote-source)s</p>") % post
        return title, content

    def handle_photo_post(self, post):
        title = title_from_content(post["photo-caption"])
        content = '<p><img src="%(photo-url-400)s"></p>%(photo-caption)s'
        content = content % post
        return title, content

    def handle_conversation_post(self, post):
        title = post["conversation-title"]
        content = post["conversation-text"].replace("\n", "<br />")
        content = "<p>%s</p>" % content
        return title, content

    def handle_video_post(self, post):
        title = title_from_content(post["video-caption"])
        content = "<p>%(video-player)s</p>" % post
        return title, content

    def handle_audio_post(self, post):
        title = post.get("id3-title")
        content = "%(audio-caption)s<p>%(audio-player)s</p>" % post
        if not title:
            title = title_from_content(post["audio-caption"])
            content = "<p>%(audio-player)s</p>" % post
        return title, content

    def handle_answer_post(self, post):
        return post["question"], post["answer"]
