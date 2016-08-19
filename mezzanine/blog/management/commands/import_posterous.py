from __future__ import unicode_literals

from datetime import datetime
import json
import time

from django.core.management.base import CommandError

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Import Tumblr blog posts into the blog app.
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "-a", "--api-token", dest="api_token",
            help="Posterous API Key")
        parser.add_argument(
            "-u", "--posterous-user", dest="username",
            help="Posterous Username")
        parser.add_argument(
            "-p", "--posterous-pass", dest="password",
            help="Posterous Password")
        parser.add_argument(
            "-d", "--posterous-host", dest="hostname",
            help="Posterous Blog Hostname (no http.. eg. 'foo.com')")

    help = "Import Posterous blog posts into the blog app."

    def request(self, path, data=None):
        try:
            import requests
        except ImportError:
            raise CommandError("Posterous importer requires the requests"
                               "library installed")
        data = data or {}
        params = {
            'api_token': self.api_token
        }
        params.update(data)
        url = "http://posterous.com/api/2/%s" % path
        r = requests.get(url,
            data=params,
            auth=(self.username, self.password)
        )
        if r.text.startswith("403"):
            raise CommandError(r.text)
        try:
            response = json.loads(r.text)
            return response
        except:
            raise CommandError(r.text)

    def handle_import(self, options):
        self.api_token = options.get("api_token")
        self.username = options.get("username")
        self.password = options.get("password")
        hostname = options.get("hostname")

        sites = self.request('sites')
        site = None
        for s in sites:
            if s['full_hostname'] == hostname:
                site = s
                time.sleep(2)
                break
        if not hostname and not site:
            if len(sites) == 1:
                site = sites[0]
            else:
                raise CommandError(
                    "Please pass your blog hostname if you have more than"
                    " one blog on your posterous account."
                )
        page = 1
        while True:
            path = 'sites/%s/posts' % site['id']
            time.sleep(2)
            posts = self.request(path, data={'page': page})
            if not posts:
                break
            for post in posts:
                content = post['body_full']
                title = post['title']
                old_url = post['full_url']
                tags = [t['name'] for t in post['tags']]
                pub_date = datetime.strptime(
                    post['display_date'][:-6],
                    "%Y/%m/%d %H:%M:%S"
                )
                self.add_post(
                    title=title,
                    content=content,
                    pub_date=pub_date,
                    tags=tags,
                    old_url=old_url
                )
                if not post['comments_count']:
                    continue
                path = "sites/%s/posts/%s/comments" % (site['id'], post['id'])
                time.sleep(2)
                comments = self.request(path)
                for comment in comments:
                    post = None
                    email = ""
                    pub_date = datetime.strptime(
                        comment['created_at'][:-6],
                        "%Y/%m/%d %H:%M:%S"
                    )
                    website = ""
                    if 'user' in comment:
                        website = comment['user']['profile_url']
                        name = comment['user']['display_name']
                    else:
                        name = comment['name']
                        website = "http://twitter.com/%s" % name
                    body = comment['body']
                    self.add_comment(
                        post=post,
                        name=name,
                        email=email,
                        pub_date=pub_date,
                        website=website,
                        body=body
                    )
            page += 1
