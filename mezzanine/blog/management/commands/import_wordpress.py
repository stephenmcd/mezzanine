
from datetime import datetime, timedelta
from optparse import make_option
from time import mktime, timezone
from xml.dom.minidom import parse

from django.core.management.base import CommandError

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Implements a Wordpress importer. Takes a file path or a URL for the
    Wordpress Extended RSS file.
    """

    option_list = BaseImporterCommand.option_list + (
        make_option("-u", "--url", dest="url",
            help="URL to import file"),
    )

    def get_text(self, xml, element, nodetype):
        """
        Gets the element's text value from the XML object provided.
        """
        rc = []
        for node in xml.getElementsByTagName(element)[0].childNodes:
            if node.nodeType == nodetype:
                rc.append(node.data)
        return "".join(rc)

    def handle_import(self, options):
        """
        Gets the posts from either the provided URL or the path if it
        is local.
        """

        url = options.get("url")

        if url is None:
            raise CommandError("Usage is import_wordpress %s" % self.args)
        try:
            import feedparser
        except ImportError:
            raise CommandError("Could not import the feedparser library.")

        feed = feedparser.parse(url)

        # we use the minidom parser as well because feedparser won't interpret
        # WXR comments correctly and ends up munging them. Lightweight DOM
        # parser is used simply to pull the comments when we get to them.
        # If someone wants to rewrite this please do.
        xml = parse(url)
        xmlitems = xml.getElementsByTagName("item")

        for (i, entry) in enumerate(feed["entries"]):
            # get a pointer to the right position in the minidom as well.
            xmlitem = xmlitems[i]
            title = entry.title
            content = entry.content[0]["value"]
            content = "<p>".join([content.replace("\n\n", "</p><p>"), "</p>"])

            # get the time struct of the published date if possible and the
            # updated date if we can"t.
            try:
                pd = entry.published_parsed
            except AttributeError:
                pd = entry.updated_parsed

            published_date = datetime.fromtimestamp(mktime(pd))
            published_date -= timedelta(seconds=timezone)

            # Only look for tags if it is't going to throw and AttributeError
            if hasattr(entry, 'tags'):
                tags = [t.term for t in entry.tags if t.scheme != "category"]

                # Tags have a tendency to not be unique in WP for
                # some reason so set the list so we have unique.
                tags = list(set(tags))
            else:
                tags = []

            # Only look for categories if it isn't going to throw an
            # AttributeError.
            if hasattr(entry, 'tags'):
                cats = [t.term for t in entry.tags if t.scheme == "category"]

                # Tags have a tendency to not be unique in WP for
                # some reason so set the list so we have unique.
                cats = list(set(cats))
            else:
                cats = []

            # create the post
            post = self.add_post(title=title, content=content,
                                 pub_date=published_date, tags=tags,
                                 categories=cats)

            # get the comments from the xml doc.
            for comment in xmlitem.getElementsByTagName("wp:comment"):
                author_name = self.get_text(comment, "wp:comment_author",
                                            comment.CDATA_SECTION_NODE)
                email = self.get_text(comment, "wp:comment_author_email",
                                      comment.TEXT_NODE)
                website = ""
                if self.get_text(comment, "wp:comment_author_url",
                                 comment.TEXT_NODE):
                    website = self.get_text(comment, "wp:comment_author_url",
                                            comment.TEXT_NODE)
                body = self.get_text(comment, "wp:comment_content",
                                     comment.CDATA_SECTION_NODE)

                comment_date = self.get_text(comment, "wp:comment_date_gmt",
                                             comment.TEXT_NODE)
                comment_date = datetime.strptime(comment_date,
                                                 "%Y-%m-%d %H:%M:%S")
                comment_date -= timedelta(seconds=timezone)

                # add the comment as a dict to the end of the comments list
                self.add_comment(post=post, name=author_name, email=email,
                    body=body, website=website, pub_date=comment_date)
