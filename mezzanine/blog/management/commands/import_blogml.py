"""
Python module to implement xml parse and import of blogml blog post data

 * Has dependency of python-dateutil
"""
from optparse import make_option
import xml.etree.ElementTree as ET

import dateutil.parser

from django.core.management.base import CommandError
from django.utils import timezone

from mezzanine.blog.management.base import BaseImporterCommand

import pytz
from pytz import UnknownTimeZoneError, timezone


class Command(BaseImporterCommand):
    """
    This class extends django management and mezzanine custom blog import
    commands to allow for import from BlogMl styled blogs
    see http://www.blogml.com/2006/09/BlogML for .x(ml)s(schema)d(efinition)
    """
    option_list = BaseImporterCommand.option_list + (
        make_option("-x", "--blogxmlfname", dest="xmlfilename",
                    help="xml file to import blog from"),
        make_option("-z", "--timezone", dest="tzinput",
                    default=timezone.get_current_timezone_name())
    )

    def handle_import(self, options):
        """
        Gets posts from provided xml dump

        - options is an optparse object with one relevent param
         * xmlfilename is for path to file
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
        tree = ET.parse(xmlfname).getroot()
        namespace = {'blogml': 'http://www.blogml.com/2006/09/BlogML'}
        postroot = tree.find('blogml:posts', namespace)
        for post in postroot.getchildren():
            post_title = post.find('blogml:title', namespace).text
            post_content = post.find('blogml:content', namespace).text
            post_categories_found = []
            post_comments_found = []
            post_categories = post.find('blogml:categories', namespace)
            post_comments = post.find('blogml:comments', namespace)
            for category in post_categories.getchildren():
                post_categories_found.append(category.attrib['ref'])
            for comments in post_comments:
                post_comments_found.append(comments.attrib[''])
            postdate = publishtz.localize(dateutil.parser.parse(
                post.attrib['date-created']))
            self.add_post(title=post_title, content=post_content,
                          pub_date=postdate, categories=post_categories_found,
                          comments=post_comments_found)

