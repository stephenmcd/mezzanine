import re
from collections import defaultdict
from datetime import datetime, timedelta
from time import mktime, timezone
from xml.dom import Node
from xml.dom.minidom import parse

from django.core.management.base import CommandError
from django.utils.html import linebreaks

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Implements a Wordpress importer. Takes a file path or a URL for the
    Wordpress Extended RSS file.
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("-u", "--url", dest="url", help="URL to import file")

    def get_text(self, xml, name):
        """
        Gets the element's text value from the XML object provided.
        """
        nodes = xml.getElementsByTagName("wp:comment_" + name)[0].childNodes
        accepted_types = [Node.CDATA_SECTION_NODE, Node.TEXT_NODE]
        return "".join(n.data for n in nodes if n.nodeType in accepted_types)

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

        # We use the minidom parser as well because feedparser won't
        # interpret WXR comments correctly and ends up munging them.
        # xml.dom.minidom is used simply to pull the comments when we
        # get to them.
        xml = parse(url)
        xmlitems = xml.getElementsByTagName("item")

        for (i, entry) in enumerate(feed["entries"]):
            # Get a pointer to the right position in the minidom as well.
            xmlitem = xmlitems[i]
            content = linebreaks(self.wp_caption(entry.content[0]["value"]))

            # Get the time struct of the published date if possible and
            # the updated date if we can't.
            pub_date = getattr(entry, "published_parsed", entry.updated_parsed)
            if pub_date:
                pub_date = datetime.fromtimestamp(mktime(pub_date))
                pub_date -= timedelta(seconds=timezone)

            # Tags and categories are all under "tags" marked with a scheme.
            terms = defaultdict(set)
            for item in getattr(entry, "tags", []):
                terms[item.scheme].add(item.term)

            if entry.wp_post_type == "post":
                post = self.add_post(
                    title=entry.title,
                    content=content,
                    pub_date=pub_date,
                    tags=terms["tag"],
                    categories=terms["category"],
                    old_url=entry.get("link", entry.id),
                )

                # Get the comments from the xml doc.
                for c in xmlitem.getElementsByTagName("wp:comment"):
                    name = self.get_text(c, "author")
                    email = self.get_text(c, "author_email")
                    url = self.get_text(c, "author_url")
                    body = self.get_text(c, "content")
                    pub_date = self.get_text(c, "date_gmt")
                    fmt = "%Y-%m-%d %H:%M:%S"
                    pub_date = datetime.strptime(pub_date, fmt)
                    pub_date -= timedelta(seconds=timezone)
                    self.add_comment(
                        post=post,
                        name=name,
                        email=email,
                        body=body,
                        website=url,
                        pub_date=pub_date,
                    )

            elif entry.wp_post_type == "page":
                old_id = getattr(entry, "wp_post_id")
                parent_id = getattr(entry, "wp_post_parent")
                self.add_page(
                    title=entry.title,
                    content=content,
                    tags=terms["tag"],
                    old_id=old_id,
                    old_parent_id=parent_id,
                )

    def wp_caption(self, post):
        """
        Filters a Wordpress Post for Image Captions and renders to
        match HTML.
        """
        for match in re.finditer(r"\[caption (.*?)\](.*?)\[/caption\]", post):
            meta = "<div "
            caption = ""
            for imatch in re.finditer(r'(\w+)="(.*?)"', match.group(1)):
                if imatch.group(1) == "id":
                    meta += 'id="%s" ' % imatch.group(2)
                if imatch.group(1) == "align":
                    meta += 'class="wp-caption %s" ' % imatch.group(2)
                if imatch.group(1) == "width":
                    width = int(imatch.group(2)) + 10
                    meta += 'style="width: %spx;" ' % width
                if imatch.group(1) == "caption":
                    caption = imatch.group(2)
            parts = (match.group(2), caption)
            meta += '>%s<p class="wp-caption-text">%s</p></div>' % parts
            post = post.replace(match.group(0), meta)
        return post
