
from datetime import datetime
from optparse import make_option
from time import sleep
from urllib import urlopen

from django.core.management.base import CommandError
from django.utils.simplejson import loads

from mezzanine.blog.management.base import BaseImporterCommand


MAX_POSTS_PER_CALL = 50 # Max number of posts Tumblr API will return per call.
MAX_RETRIES_PER_CALL = 3 # Max times to retry API call after failing.
SLEEP_PER_RETRY = 3 # Seconds to pause for between retries.


class Command(BaseImporterCommand):
    """
    Import Tumblr blog posts into the blog app.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-t", "--tumblr-user", dest="tumblr_user",
            help="Tumblr username"),
    )
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
                    print "Calling %s" % call_url
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
            except IOError, e:
                error = "Error communicating with Tumblr API (%s)" % e
                raise CommandError(error)

            data = response.read()
            json = loads(data.split(json_start, 1)[1].strip().rstrip(";"))
            posts = json["posts"]
            start_index += MAX_POSTS_PER_CALL

            if not posts:
                break
            for post in posts:
                if post["type"] == "regular":
                    pub_date = datetime.strptime(post["date"], date_format)
                    self.add_post(title=post["regular-title"],
                        content=post["regular-body"], pub_date=pub_date, 
                        tags=post.get("tags"), old_url=post["url-with-slug"])
