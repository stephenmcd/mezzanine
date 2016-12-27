"""
Python module to implement xml parse and import of blogml blog post data

 * Has dependency of python-dateutil
"""
import xml.etree.ElementTree as ET

import pytz
from dateutil.parser import parse
from django.core.management.base import CommandError
from django.utils import timezone
from pytz import UnknownTimeZoneError, timezone

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    This class extends django management and mezzanine custom blog import
    commands to allow for import from BlogMl styled blogs
    see http://www.blogml.com/2006/09/BlogML for .x(ml)s(schema)d(efinition)
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "-x", "--xmldumpfname", dest="xmlfilename", help="xml file to import blog from"
        )

        parser.add_argument(
            "-z", "--timezone", dest="tzinput",
            default=timezone.get_current_timezone_name()
        )

    def handle_import(self, options):
        """
        Gets posts from provided xml dump

        - options is an optparse object with one relevant param
         * xmlfname is for path to file
        """
        xmlfname = options.get("xmlfilename")
        tzinput = options.get("tzinput")
        # validate xml name entered
        if xmlfname is None:
            raise CommandError("Usage is import_blogml %s" % self.args)

        # timezone related error handling
        # valid string input check, import check
        try:
            publishtz = pytz.timezone(tzinput)
        except ImportError:
            raise CommandError("Could not import the pytz library")
        except UnknownTimeZoneError:
            raise CommandError("Unknown Time Zone entered, see pytz for" +
                               "list of acceptable strings")

        # parsing xml tree and populating variables for post addition
        tree = ET.parse(xmlfname)
        # namespace for easier searching
        ns = {"blogml": "http://www.blogml.com/2006/09/BlogML"}
        # valid xpaths to find relevant items
        # finds posts from root
        search_paths = {"find_posts": ".blogml:posts/blogml:post",
                        # finds comments on a given post element
                        "find_comments": ".blogml:comments/blogml:comment",
                        # finds categories on a given post element and from root
                        "find_categories": "blogml:categories/blogml:category",
                        # finds tags on a given post element
                        "find_tags": "blogml:tags/blogml:tag"}
        # empty found dict to be used mutably in post addition
        found = {}
        # find all categories in root, get titles and ref id"s
        cat_elements = tree.findall(search_paths["find_categories"], namespaces=ns)
        # gather ref id"s on root categories into tuple
        cat_ids = tuple((x.attrib["id"] for x in cat_elements))
        # gather category text from title element on root categories into tuple
        cat_title_txt = tuple((x.find("blogml:title", namespaces=ns).text for x in cat_elements))
        # map into dictionary of key=category_id as hash, and value=category title text
        categories_found = dict(zip(cat_ids, cat_title_txt))
        # find all posts in root
        posts_found = tree.findall(search_paths["find_posts"], namespaces=ns)
        for post in posts_found:
            """
            By iterating on posts, extract critical information for post addition.
            - title is extracted as child of post element, text value within tag
            - content is extracted as child of post element, text value within tag
            - post-url is extracted as attribute of post element with key post-url
            - date-created is extracted as attribute of post element with name date-created and converted to datetime
                with key date-created
            - categories are found through dict-key comparison to parent found categories, list value for key categories
            - tags are found as grandchildren of post and children of tag with attribute ref as a text description
            """
            found["title"] = post.find("blogml:title", namespaces=ns).text
            found["content"] = post.find("blogml:content", namespaces=ns).text
            found["post-url"] = post.attrib["post-url"]
            found["date-created"] = parse(post.attrib["date-created"])
            post_category_refs = [x.attrib["ref"] for x in post.findall(search_paths["find_categories"])]
            found["categories"] = list((categories_found[x] for x in post_category_refs))
            found["tags"] = [x.attrib["ref"] for x in post.findall("blogml:tags/blogml:tag", namespaces=ns)]
            post_entered = self.add_post(title=found["title"], content=found["content"], old_url=found["post-url"],
                                         pub_date=found["date-created"], categories=found["categories"])
            found.clear()
            comments_found = post.findall(search_paths["find_comments"])
            cmmnt = {}
            for comment in comments_found:
                """
                By iterating on comments within single post, extract information for comment addition on post
                - name of user extracted as attribute of comment element, key name
                - email of user extracted as attribute of comment element, key email
                - pub_date of comment extracted as attribute of comment element, datetime parsed, key pub_date
                - website of comment extracted as attribute of comment element, key website
                - body of comment extracted as text of child content tag on comment, key body
                """
                cmmnt["name"] = comment.attrib["user-name"]
                cmmnt["email"] = comment.attrib["user-email"]
                cmmnt["pub_date"] = parse(comment.attrib["date-created"])
                cmmnt["website"] = comment.attrib["user-url"]
                cmmnt["body"] = comment.find("blogml:content").text
                self.add_comment(post=post_entered, name=cmmnt["name"], email=cmmnt["email"],
                                 pub_date=cmmnt["pub_date"],
                                 website=cmmnt["website"], body=cmmnt["body"])
                cmmnt.clear()
