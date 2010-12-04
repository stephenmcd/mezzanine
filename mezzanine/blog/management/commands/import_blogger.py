
from datetime import datetime, timedelta
from optparse import make_option
from time import timezone

from django.core.management.base import CommandError

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Implements a Blogger importer. Takes a Blogger ID in order to be able to
    determine which blog it should point to and harvest the XML from.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-b", "--blogger-id", dest="blog_id",
            help="Blogger Blog ID from blogger dashboard"),
    )

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
        query = service.Query()
        query.feed = "/feeds/%s/posts/full" % blog_id
        query.max_results = 500
        try:
            feed = blogger.Get(query.ToUri())
        except service.RequestError, err:
            message = "There was a service error. The response was: " \
                "%(status)s %(reason)s - %(body)s" % err.message
            raise CommandError(message, blogger.server + query.feed,
                               err.message["status"])

        for (i, entry) in enumerate(feed.entry):
            # this basically gets the unique post ID from the URL to itself
            # and pulls the ID off the end.
            post_id = entry.GetSelfLink().href.split("/")[-1]
            title = entry.title.text
            content = entry.content.text
            #this strips off the time zone info off the end as we want UTC
            published_date = datetime.strptime(entry.published.text[:-6],
                    "%Y-%m-%dT%H:%M:%S.%f") - timedelta(seconds=timezone)

            #TODO - issues with content not generating correct <P> tags

            tags = [tag.term for tag in entry.category]
            post = self.add_post(title=title, content=content,
                                 pub_date=published_date, tags=tags)

            # get the comments from the post feed and then add them to
            # the post details
            ids = (blog_id, post_id)
            comment_url = "/feeds/%s/%s/comments/full?max-results=1000" % ids
            comments = blogger.Get(comment_url)

            for comment in comments.entry:
                email = comment.author[0].email.text
                author_name = comment.author[0].name.text
                #this strips off the time zone info off the end as we want UTC
                comment_date = datetime.strptime(comment.published.text[:-6],
                    "%Y-%m-%dT%H:%M:%S.%f") - timedelta(seconds=timezone)
                website = ""
                if comment.author[0].uri:
                    website = comment.author[0].uri.text
                body = comment.content.text

                # add the comment as a dict to the end of the comments list
                self.add_comment(post=post, name=author_name, email=email,
                    body=body, website=website, pub_date=comment_date)
