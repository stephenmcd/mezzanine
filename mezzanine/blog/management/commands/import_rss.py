
from datetime import timedelta
from optparse import make_option
from time import timezone

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Import an RSS feed into the blog app.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-r", "--rss-url", dest="rss_url",
            help="RSS feed URL"),
    )
    help = "Import an RSS feed into the blog app."

    def handle_import(self, options):
        from dateutil import parser
        from feedparser import parse

        posts = parse(options.get("rss_url"))["entries"]
        for post in posts:
            tags = [tag["term"] for tag in post.tags]

            pub_date = parser.parse(post.updated)
            pub_date -= timedelta(seconds=timezone)
            self.add_post(title=post.title, content=post.content[0]["value"],
                          pub_date=pub_date, tags=tags, old_url=None)
