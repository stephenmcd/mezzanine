"""
Imports blog posts from a BlogMl file.

Dependends on python-dateutil being installed.
"""
import xml.etree.ElementTree

from django.core.management.base import CommandError
from django.utils import timezone

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Imports blog posts from a BlogMl file.
    See http://www.blogml.com/2006/09/BlogML for more info.
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "-x", "--xmldumpfname", dest="xmlfilename",
            help="xml file to import blog from"
        )

    def handle_import(self, options):
        """
        Gets posts from provided xml dump.
        """

        try:
            from dateutil.parser import parse
        except ImportError:
            raise CommandError("dateutil package is required")

        xmlfname = options.get("xmlfilename")
        set_tz = timezone.get_current_timezone()
        # parsing xml tree and populating variables for post addition
        tree = xml.etree.ElementTree.parse(xmlfname)
        # namespace for easier searching
        ns = {"blogml": "http://www.blogml.com/2006/09/BlogML"}
        search_paths = {"find_posts": ".blogml:posts/blogml:post",
                        "find_comments": ".blogml:comments/blogml:comment",
                        "find_categories": "blogml:categories/blogml:category",
                        "find_tags": "blogml:tags/blogml:tag"}

        def _process_post_element(post_element, blog_categories):
            """
            Converts post BlogML element into post data.
            """
            post_dict = dict()
            post_dict["title"] = post_element.find("blogml:title",
                                                   namespaces=ns).text
            post_dict["content"] = post_element.find("blogml:content",
                                                     namespaces=ns).text
            post_dict["post-url"] = post_element.attrib["post-url"]
            post_dict["date-created"] = parse(
                post_element.attrib["date-created"]
            ).replace(tzinfo=set_tz)
            post_category_refs = [
                cat_element.attrib["ref"] for cat_element in
                post_element.findall(
                    search_paths["find_categories"],
                    namespaces=ns
                )
                ]
            post_dict["categories"] = list(
                (blog_categories[category_id] for category_id in
                 post_category_refs))
            post_dict["tags"] = [x.attrib["ref"] for x in
                                 post_element.findall("blogml:tags/blogml:tag",
                                                      namespaces=ns)
                                 ]
            return post_dict

        def _process_comment_element(comment_element):
            """
            Converts comment BlogML element into comment data.
            """
            comment_dict = dict()
            comment_dict["name"] = comment_element.attrib["user-name"]
            comment_dict["email"] = comment_element.attrib["user-email"]
            comment_dict["pub_date"] = parse(
                comment_element.attrib["date-created"]
            ).replace(tzinfo=set_tz)
            comment_dict["website"] = comment_element.attrib["user-url"]
            comment_dict["body"] = comment_element.find("blogml:content",
                    namespaces=ns).text
            return comment_dict

        def _process_categories(root_tree):
            """
            Finds all categories within BlogMl root tree
            """
            cat_elements = root_tree.findall(search_paths["find_categories"],
                                             namespaces=ns)
            cat_ids = tuple((x.attrib["id"] for x in cat_elements))
            cat_title_txt = tuple(
                (x.find("blogml:title", namespaces=ns).text
                 for x in cat_elements))
            categories_dict = dict(zip(cat_ids, cat_title_txt))
            return categories_dict

        categories_found = _process_categories(tree)
        posts_found = tree.findall(search_paths["find_posts"], namespaces=ns)

        for post in posts_found:
            post_info = _process_post_element(post, categories_found)
            post_entered = self.add_post(title=post_info["title"],
                                         content=post_info["content"],
                                         old_url=post_info["post-url"],
                                         pub_date=post_info["date-created"],
                                         categories=post_info["categories"])
            comments_found = post.findall(search_paths["find_comments"],
                                          namespaces=ns)
            for comment in comments_found:
                comment_info = _process_comment_element(comment)
                self.add_comment(post=post_entered, name=comment_info["name"],
                                 email=comment_info["email"],
                                 pub_date=comment_info["pub_date"],
                                 website=comment_info["website"],
                                 body=comment_info["body"])
