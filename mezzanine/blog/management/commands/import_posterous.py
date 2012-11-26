from mezzanine.blog.management.base import BaseImporterCommand
from optparse import make_option
import json
import time
from datetime import datetime
import sys


class PosterousImportException(Exception):
    pass


class Command(BaseImporterCommand):
    """
    Import Tumblr blog posts into the blog app.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-a", "--api-token", dest="api_token",
            help="Posterous API Key"),
        make_option("-u", "--posterous-user", dest="username",
            help="Posterous Username"),
        make_option("-p", "--posterous-pass", dest="password",
            help="Posterous Password"),
        make_option("-d", "--posterous-host", dest="hostname",
            help="Posterous Blog Hostname (no http.. eg. 'foo.com')"
        ),
    )
    help = "Import Posterous blog posts into the blog app."

    def request(self, path, data=None):
        import requests
        my_config = {'verbose': sys.stderr}
        data = data or {}
        params = {
            'api_token': self.api_token
        }
        params.update(data)
        url = "http://posterous.com/api/2/%s" % path
        r = requests.get(url,
            data=params,
            auth=(self.username, self.password),
            config=my_config
        )
        if r.text.startswith("403"):
            raise PosterousImportException(r.text)
        try:
            response = json.loads(r.text)
            return response
        except:
            raise PosterousImportException(r.text)

    def handle_import(self, options):
        self.api_token = options.get("api_token")
        self.username = options.get("username")
        self.password = options.get("password")
        hostname = options.get("hostname")

        sites = self.request('sites')
        site = None
        for s in sites:
            if s['full_hostname'] == hostname:
                time.sleep(2)
                break
        if not hostname and not site:
            if len(sites) == 1:
                site = sites[0]
            else:
                raise PosterousImportException(
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
