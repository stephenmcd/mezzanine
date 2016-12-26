"""
Python module to implement xml parse and import of blogml blog post data

 * Has dependency of python-dateutil
"""
from optparse import make_option

import dateutil.parser

from django.core.management.base import CommandError
from django.utils import timezone

from mezzanine.blog.management.base import BaseImporterCommand


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
            import pytz
            from pytz import UnknownTimeZoneError
            publishtz = pytz.timezone(tzinput)
        except ImportError:
            raise CommandError("Could not import the pytz library")
        except UnknownTimeZoneError:
            raise CommandError("Unknown Time Zone entered, see pytz for" +
                               "list of acceptable strings")

        try:
            import xml.etree.ElementTree as ET
        except ImportError:
            raise CommandError("Could not import the xml ElementTree library")

        # parsing xml tree and populating variables for post addition
        tree = ET.parse(xmlfname).getroot()
        namespace = {'blogml': 'http://www.blogml.com/2006/09/BlogML'}
        postroot = tree.find('blogml:posts', namespace)
        for post in postroot.getchildren():
            posttitle = post.find('blogml:title', namespace).text
            postcontent = post.find('blogml:content', namespace).text
            postcategoriesfound = []
            postcategories = post.find('blogml:categories', namespace)
            post_comments = post.find('blogml:comments', namespace)
            for category in postcategories.getchildren():
                postcategoriesfound.append(category.attrib['ref'])
            for comments in
            postdate = publishtz.localize(dateutil.parser.parse(
                post.attrib['date-created']))
            self.add_post(title=posttitle, content=postcontent,
                          pub_date=postdate, categories=postcategoriesfound
                          comments=post_comments_found)

