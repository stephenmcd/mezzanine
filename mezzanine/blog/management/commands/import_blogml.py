"""
Python module to implement xml parse and import of blogml blog post data

 * Has dependency of python-dateutil
"""
import xml.etree.ElementTree

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
            "-x", "--xmldumpfname", dest="xmlfilename",
            help="xml file to import blog from"
        )

    def handle_import(self, options):
        """
        Gets posts from provided xml dump

        - options is an optparse object with one relevant param
         * xmlfname is for path to file
        """

        try:
            from dateutil.parser import parse
        except ImportError:
            raise ImportError("python-dateutil must be installed; dateutil "
                              "missing")

        xmlfname = options.get("xmlfilename")
        # parsing xml tree and populating variables for post addition
        tree = xml.etree.ElementTree.parse(xmlfname)
        # namespace for easier searching
        ns = {"blogml": "http://www.blogml.com/2006/09/BlogML"}
        # valid xpaths to find relevant items
        #               # finds posts from root
        search_paths = {"find_posts": ".blogml:posts/blogml:post",
                        # finds comments on a given post element
                        "find_comments": ".blogml:comments/blogml:comment",
                        # finds categories on a given post element and from
                        # root
                        "find_categories": "blogml:categories/blogml:category",
                        # finds tags on a given post element
                        "find_tags": "blogml:tags/blogml:tag"}

        def _process_post_element(post_element, blog_categories):
            """
            Extract critical information for post addition.
            - title is extracted as child of post element, text value within
              tag
            - content is extracted as child of post element, text value within
              tag
            - post-url is extracted as attribute of post element with key
              post-url
            - date-created is extracted as attribute of post element with name
              date-created and converted to datetime with key date-created
            - categories are found through dict-key comparison to parent found
              categories, list value for key categories
            - tags are found as grandchildren of post and children of tag with
              attribute ref as a text description
            """
            post_dict = dict()
            post_dict["title"] = post_element.find("blogml:title",
                                                   namespaces=ns).text
            post_dict["content"] = post_element.find("blogml:content",
                                                     namespaces=ns).text
            post_dict["post-url"] = post_element.attrib["post-url"]
            post_dict["date-created"] = parse(
                post_element.attrib["date-created"]
            )
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
            Extract comment information given comment element
            - name of user extracted as attribute of comment element,
              key name
            - email of user extracted as attribute of comment element,
              key email
            - pub_date of comment extracted as attribute of comment
              element, datetime parsed, key pub_date
            - website of comment extracted as attribute of comment element,
              key website
            - body of comment extracted as text of child content tag
              on comment, key body
            - returns comment_dict object for use in iteration over blog tree
            """
            comment_dict = dict()
            comment_dict["name"] = comment_element.attrib["user-name"]
            comment_dict["email"] = comment_element.attrib["user-email"]
            comment_dict["pub_date"] = parse(
                comment_element.attrib["date-created"]
            )
            comment_dict["website"] = comment_element.attrib["user-url"]
            comment_dict["body"] = comment_element.find("blogml:content",
                    namespaces=ns).text
            return comment_dict

        def _process_categories(root_tree):
            """
            find all categories within BlogMl root tree
            :param root_tree: root tree element to search for categories on
            :return: dict of categories by UID and category text
            """
            # find all categories in root, get titles and ref id"s
            cat_elements = root_tree.findall(search_paths["find_categories"],
                                             namespaces=ns)
            # gather ref id"s on root categories into tuple
            cat_ids = tuple((x.attrib["id"] for x in cat_elements))
            # gather category text from title element on
            # root categories into tuple
            cat_title_txt = tuple(
                (x.find("blogml:title", namespaces=ns).text
                 for x in cat_elements))
            # map into dictionary of key=category_id as hash,
            # and value=category title text
            categories_dict = dict(zip(cat_ids, cat_title_txt))
            return categories_dict

        # find all categories in root tree of blog
        categories_found = _process_categories(tree)
        # find all posts in root tree of blog
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
