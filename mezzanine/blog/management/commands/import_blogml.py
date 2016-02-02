"""
Python module to implement xml parse and import of blogml blog post data
"""
from optparse import make_option
import dateutil.parser
from django.core.management.base import CommandError
from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    This class extends django management and mezzanine custom blog import
    commands to allow for import from blogml styled blogs
    Should supply user to upload as and xmlfilename and a timezone
    """
    option_list = BaseImporterCommand.option_list + (
        make_option("-x", "--blogxmlfname", dest="xmlfilename",
                    help="xml file to import blog from BoxAlly"),
        make_option("-t", "--timezone", dest="tzchoice",
                    help="timezone utilized")
    )

    def handle_import(self, options):
        """
        Gets posts from provided xml dump
        TODO: Handle comment importing

        - options is an optparse object with two relevent params
         * xmlfilename is for path to file
         * tzchoice is for timezone of published post and localization
        """
        xmlfname = options.get("xmlfilename")
        tzchoice = options.get("tzchoice")
        # validate xml name entered
        if xmlfname is None:
            raise CommandError("Usage is import_blogml %s" % self.args)

        # timezone related error handling
        # valid string input check, import check
        try:
            import pytz
            publishtz = pytz.timezone(tzchoice)
        except NameError:
            raise CommandError("Please select a valid timezone " +
                               "(see pytz for possible values)")
        except ImportError:
            raise CommandError("Could not import the pytz library")

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
            for category in postcategories.getchildren():
                postcategoriesfound.append(category.attrib['ref'])
            postdate = publishtz.localize(dateutil.parser.parse(
                post.attrib['date-created']))
            self.add_post(title=posttitle, content=postcontent,
                          pub_date=postdate, categories=postcategoriesfound)
