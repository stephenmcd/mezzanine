
from datetime import timedelta
from optparse import make_option
from time import timezone

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Import an RSS feed into the blog app.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-d", "--drupal-url", dest="drupal_url",
            help="Drupal blog URL"),
    )
    help = "Import a drupal blog into the blog app."

    def handle_import(self, options):
        from dateutil import parser
        from feedparser import parse
        from mechanize import Browser
        from BeautifulSoup import BeautifulSoup
        b = Browser()
        url = options.get("drupal_url")
        response = b.open(url)
        html = response.read()
        soup = BeautifulSoup(html)
        links = soup.findAll('link')
        for link in links:
            if link['type'].startswith('application/rss'):
                rssurl = link['href']
                print rssurl
                break
        posts = parse(rssurl).entries
        for post in posts:
            pub_date = parser.parse(post.updated)
            pub_date -= timedelta(seconds=timezone)
            self.add_post(title=post.title, content=post['summary_detail']['value'],
                         pub_date=pub_date, tags=None, old_url=None)
            
