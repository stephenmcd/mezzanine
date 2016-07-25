from __future__ import unicode_literals

from datetime import datetime, timedelta
from time import timezone
import re

from django.core.management.base import CommandError

from mezzanine.blog.management.base import BaseImporterCommand


# TODO: update this to use v3 of the blogger API.
class Command(BaseImporterCommand):
    """
    Implements a Blogger importer. Takes a Blogger ID in order to be able to
    determine which blog it should point to and harvest the XML from.
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "-b", "--blogger-id", dest="blog_id",
            help="Blogger Blog ID from blogger dashboard")

    def handle_import(self, options):
        """
        Gets posts from Blogger.
        """

        blog_id = options.get("blog_id")
        if blog_id is None:
            raise CommandError("Usage is import_blogger %s" % self.args)

        try:
            from gdata import service
        except ImportError:
            raise CommandError("Could not import the gdata library.")

        blogger = service.GDataService()
        blogger.service = "blogger"
        blogger.server = "www.blogger.com"

        start_index = 1
        processed_posts = []
        new_posts = 1

        while new_posts:
            new_posts = 0

            query = service.Query()
            query.feed = "/feeds/%s/posts/full" % blog_id
            query.max_results = 500
            query.start_index = start_index

            try:
                feed = blogger.Get(query.ToUri())
            except service.RequestError as err:
                message = "There was a service error. The response was: " \
                    "%(status)s %(reason)s - %(body)s" % err.message
                raise CommandError(message, blogger.server + query.feed,
                                   err.message["status"])

            for (i, entry) in enumerate(feed.entry):
                # this basically gets the unique post ID from the URL to itself
                # and pulls the ID off the end.
                post_id = entry.GetSelfLink().href.split("/")[-1]

                # Skip duplicate posts. Important for the last query.
                if post_id in processed_posts:
                    continue

                title = entry.title.text
                content = entry.content.text
                # this strips off the time zone info off the end as we want UTC
                clean_date = entry.published.text[:re.search(r"\.\d{3}",
                    entry.published.text).end()]

                published_date = self.parse_datetime(clean_date)

                # TODO - issues with content not generating correct <P> tags

                tags = [tag.term for tag in entry.category]
                post = self.add_post(title=title, content=content,
                                     pub_date=published_date, tags=tags)

                # get the comments from the post feed and then add them to
                # the post details
                comment_url = "/feeds/%s/%s/comments/full?max-results=1000"
                comments = blogger.Get(comment_url % (blog_id, post_id))

                for comment in comments.entry:
                    email = comment.author[0].email.text
                    author_name = comment.author[0].name.text
                    # Strip off the time zone info off the end as we want UTC
                    clean_date = comment.published.text[:re.search(r"\.\d{3}",
                        comment.published.text).end()]

                    comment_date = self.parse_datetime(clean_date)

                    website = ""
                    if comment.author[0].uri:
                        website = comment.author[0].uri.text
                    body = comment.content.text

                    # add the comment as a dict to the end of the comments list
                    self.add_comment(post=post, name=author_name, email=email,
                                     body=body, website=website,
                                     pub_date=comment_date)

                processed_posts.append(post_id)
                new_posts += 1

            start_index += 500

    def parse_datetime(self, datetime_string):
        try:
            parsed_datetime = datetime.strptime(datetime_string,
                                                "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            parsed_datetime = datetime.strptime(datetime_string,
                                                "%Y-%m-%dT%H:%M:%S")

        parsed_datetime -= timedelta(seconds=timezone)
        return parsed_datetime
