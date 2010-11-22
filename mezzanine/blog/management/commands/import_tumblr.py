
from datetime import datetime
from optparse import make_option
from urllib import urlopen

from django.core.management.base import CommandError
from django.utils.simplejson import loads

from mezzanine.blog.management.base import BaseImporterCommand


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
        json_url = "http://%s.tumblr.com/api/read/json" % tumblr_user
        try:
            response = urlopen(json_url)
            if response.code == 404:
                raise CommandError("Invalid Tumblr user.")
            elif response.code == 503:
                raise CommandError("Tumblr API currently unavailable, "
                                   "try again shortly.")
            elif response.code != 200:
                raise IOError("HTTP status %s" % response.code)
        except IOError, e:
            raise CommandError("Error communicating with Tumblr API (%s)" % e)

        start = "var tumblr_api_read ="
        date_format = "%a, %d %b %Y %H:%M:%S"
        json = loads(response.read().split(start, 1)[1].strip().rstrip(";"))
        for entry in json["posts"]:
            if entry["type"] == "regular":
                published_date = datetime.strptime(entry["date"], date_format)
                self.add_post(title=entry["regular-title"],
                    content=entry["regular-body"], pub_date=published_date, 
                    tags=entry.get("tags"), old_url=entry["url-with-slug"])
