from __future__ import unicode_literals

from datetime import timedelta
from optparse import make_option
from time import timezone
try:
    from urllib.request import urlopen
    from urllib.parse import urljoin
except ImportError:
    from urllib import urlopen
    from urlparse import urljoin

from django.core.management.base import CommandError

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Import an RSS feed into the blog app.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-r", "--rss-url", dest="rss_url",
            help="RSS feed URL"),
        make_option("-p", "--page-url", dest="page_url",
            help="URL for a web page containing the RSS link"),
    )
    help = ("Import an RSS feed into the blog app. Requires the "
            "dateutil and feedparser packages installed, and also "
            "BeautifulSoup if using the --page-url option.")

    def handle_import(self, options):

        rss_url = options.get("rss_url")
        page_url = options.get("page_url")
        if not (page_url or rss_url):
            raise CommandError("Either --rss-url or --page-url option "
                               "must be specified")

        try:
            from dateutil import parser
        except ImportError:
            raise CommandError("dateutil package is required")
        try:
            from feedparser import parse
        except ImportError:
            raise CommandError("feedparser package is required")
        if not rss_url and page_url:
            try:
                from BeautifulSoup import BeautifulSoup
            except ImportError:
                raise CommandError("BeautifulSoup package is required")
            for l in BeautifulSoup(urlopen(page_url).read()).findAll("link"):
                if ("application/rss" in l.get("type", "") or
                    "application/atom" in l.get("type", "")):
                    rss_url = urljoin(page_url, l["href"])
                    break
            else:
                raise CommandError("Could not parse RSS link from the page")

        posts = parse(rss_url)["entries"]
        for post in posts:
            if hasattr(post, 'content'):
                content = post.content[0]["value"]
            else:
                content = post.summary
            tags = [tag["term"] for tag in getattr(post, 'tags', [])]
            pub_date = parser.parse(post.updated)
            pub_date -= timedelta(seconds=timezone)
            self.add_post(title=post.title, content=content,
                          pub_date=pub_date, tags=tags, old_url=None)
