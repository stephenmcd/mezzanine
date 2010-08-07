
from datetime import datetime
from urllib import urlopen
from urlparse import urlparse

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils.simplejson import loads


class Command(BaseCommand):
    """
    Import Tumblr blog posts into the blog app.
    """

    help = "Import Tumblr blog posts into the blog app."
    args = "tumblr_user mezzanine_user"

    def handle(self, tumblr_user="", mezzanine_user="", *args, **options):

        json_url = "http://%s.tumblr.com/api/read/json" % tumblr_user
        if not (tumblr_user and mezzanine_user):
            raise CommandError("Usage is import_tumblr %s" % self.args)
        try:
            response = urlopen(json_url)
            if response.code != 200:
                raise IOError
        except IOError:
            raise CommandError("Invalid Tumblr user")
        if mezzanine_user is not None:
            try:
                mezzanine_user = User.objects.get(username=mezzanine_user)
            except User.DoesNotExist:
                raise CommandError("Invalid Mezzanine user")

        from mezzanine.blog.models import BlogPost
        from mezzanine.core.models import Keyword
        from mezzanine.settings import CONTENT_STATUS_PUBLISHED
        site = Site.objects.get_current()
        start = "var tumblr_api_read ="
        date_format = "%a, %d %b %Y %H:%M:%S"
        json = loads(response.read().split(start, 1)[1].strip().rstrip(";"))
        for entry in json["posts"]:
            if entry["type"] == "regular":
                print "Importing %s" % entry["regular-title"]
                post, created = BlogPost.objects.get_or_create(
                    user=mezzanine_user, title=entry["regular-title"],
                    content=entry["regular-body"],
                    status=CONTENT_STATUS_PUBLISHED,
                    publish_date=datetime.strptime(entry["date"], date_format))
                for tag in entry["tags"]:
                    keyword, created = Keyword.objects.get_or_create(value=tag)
                    post.keywords.add(keyword)
                post.set_searchable_keywords()
                redirect, created = Redirect.objects.get_or_create(site=site,
                    old_path=urlparse(entry["url-with-slug"]).path)
                redirect.new_path = urlparse(post.get_absolute_url()).path
                redirect.save()
