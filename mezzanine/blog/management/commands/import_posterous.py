from mezzanine.blog.management.base import BaseImporterCommand
from optparse import make_option
from urllib import urlopen, urlencode
import requests
import json
import time
from datetime import datetime
import sys
# import requests_cache
# requests_cache.configure('demo_cache')

class PosterousImportException(Exception):
    pass

class Command(BaseImporterCommand):
    """
    Import Tumblr blog posts into the blog app.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-a", "--api-token", dest="api_token",
            help="Posterous API Key"),
        make_option("-u", "--username", dest="username",
            help="Posterous Username"),
        make_option("-p", "--password", dest="password",
            help="Posterous Password"),
        make_option("-d", "--hostname", dest="hostname",
            help="Posterous Blog Hostname")
    )
    help = "Import Posterous blog posts into the blog app."

    def request(self, path, data=None):
        my_config = {'verbose': sys.stderr}
        data = data or {}
        params = {
            'api_token': self.api_token
        }
        params.update(data)
        url = "http://posterous.com/api/2/%s" % path
        r = requests.get(url, data=params, auth=(self.username, self.password), config=my_config)
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
        for site in sites:
            if site['full_hostname'] == hostname:
                time.sleep(2)
                break

        path ='sites/%s/posts' % site['id']
        page = 1
        while True:
            posts = self.request(path, data={'page': page})
            print len(posts)
            if not posts:
                break
            for post in posts:
                # import pprint
                # print pprint.pprint(post)
                content = post['body_full']
                title = post['title']
                old_url = post['full_url']
                tags = [t['name'] for t in post['tags']]
                pub_date = datetime.strptime(post['display_date'][:-6], "%Y/%m/%d %H:%M:%S")
                self.add_post(
                    title=title,
                    content=content,
                    pub_date=pub_date,
                    tags=tags,
                    old_url=old_url
                )
            page += 1
            time.sleep(2)


