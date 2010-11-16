"""
Importer handler used to import blogs into mezzanine
"""

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Import Blog Posts into mezzanine from a variety of different sources
    """
    
    option_list = BaseCommand.option_list + (
        make_option("-t", "--blogtype", dest="blogtype", 
            help="Type of blog to parse. [blogger, wordpress, tumblr]"),
        make_option("-b", "--blogger", dest="blog_id",
            help="Blogger Blog ID from blogger dashboard"),
        make_option("-u", "--url", dest="url",
            help="URL to import file"),
        make_option("-r", "--tumblr", dest="tumblruser",
            help="Tumblr user id"),
        make_option("-m", "--mezzanine-user", dest="mezzanine_user",
            help="Mezzanine username to assign the imported blog posts into"),
    )
    
    
    def handle(self, *args, **options):
        from mezzanine.blog import importers

        blogtype = options["blogtype"]   
        mezzuser = options["mezzanine_user"]
        
        if mezzuser==None:
            raise CommandError("Please ensure a mezzanine user is specified")

        # care of Stephen McD
        # check the objects in the importer module and compare it against the
        # blog type.
        importer_classes=[getattr(importers, x) for x in 
            dir(importers) if x.lower()==blogtype]
        if importer_classes:
            importer_class = importer_classes[0]

            if issubclass(importer_class, importers.Importer):

                blogimport = importer_class(**options)
                blogimport.convert()
                blogimport.process(mezzanine_user=mezzuser)
            else:
                raise CommandError("Blog type seems to be wrong")
    
    def usage(self, *args):
    
        usagenotes= """
        Imports blog posts and comments into mezzanine from a variety of different sources
        
        %prog importer --blogtype=[] [options] --mezzanine-user=[...]
        
        eg: WordPress
        %prog importer -t=wordpress [--filepath=[...] | --url=[..]] -m=[...]
        
        eg: Blogger
        %prog importer -t=blogger [--blogger=[...]] -m=[...]
        
        eg: Tumblr (currently todo)
        %prog importer -t=tumblr [--tumblr=[...]] -m=[...]
        """
    
        return usagenotes
