"""
Base importer class for the commands to pull in blog posts from other blog 
platforms into Mezzanine.
"""

from datetime import datetime, timedelta
from time import mktime, strftime, strptime, timezone
from optparse import make_option
from xml.dom.minidom import parse, parseString

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.core.models import Keyword, CONTENT_STATUS_PUBLISHED


class Error(CommandError):
    """
    Base class for errors in this module.
    """
    pass
    

class EmptyFeedError(Error):
    """
    Exception raised for the case where a valid feed has returned no posts.
    
    Attributes:
        msg: explanation of the error
        url: the feed url that was called
    """
    def __init__(self, msg, url):
        self.msg = msg
        self.url = url


class FeedURLError(Error):
    """
    Exception raised in the case where the URL that is hit for the feed 
    doesn't return correctly at all.
    
    Attributes:
        http_code: http response code returned
        msg: explanation of the error
        url: url that was called
    """
    def __init__(self, msg, url, http_code):
        self.msg = msg
        self.url = url
        self.http_code = http_code
        
    def __str__(self):
        data = self.msg + " " + self.url
        return data


class EmptyPostError(Error):
    """
    Exception raised in the case where a comment is being attempted to be
    added to an post that has not been specified.
    """
    def __str__(self):
        return "Attempted to add a comment to no post."


class BaseImporterCommand(BaseCommand):
    """
    Imports blog posts into Mezzanine from a variety of different sources. 
    Should be subclasses for a particular blogging platform and have the 
    ``handle_import`` method overrdden to provide the import mechanism 
    specific to the blogging platform being dealt with.
    """
    
    option_list = BaseCommand.option_list + (
        make_option("-m", "--mezzanine-user", dest="mezzanine_user",
            help="Mezzanine username to assign the imported blog posts to."),
    )

    def __init__ (self, **kwargs):
        self.posts = []
        super(BaseImporterCommand, self).__init__(**kwargs)
        
    def add_post(self, title=None, author=None, pub_date=None, tags=None,
        content=None, comments=None):
        """
        Adds a post to the post list for processing.
        
        Attributes:
            pub_date is assumed to be a datetime struct
        """
        if not comments:
            comments = []
        print "Retrieved post titled: %s" % title
        self.posts.append({
            "title": title,
            "publication_date": pub_date,
            "content": content,
            "tags": tags,
            "comments": comments})
        return self.posts[-1]
                
    def add_comment(self, post=None, name=None, email=None, pub_date=None, 
        website=None, body=None):
        """
        Adds a comment to the post provided.
        
        Attributes:
            pub_date is assumed to be a date time struct
        """
        print "Retrieved comment by: %s" % name
        if not post:
            raise (EmptyPostError)
        else:
            post["comments"].append({
                "name": name,
                "email": email,
                "time_created": pub_date,
                "website": website,
                "body": body,
            })
            
    def handle(self, *args, **options):
        """
        Processes the converted data into the Mezzanine database correctly.
        
        Attributes:
            mezzanine_user: the user to put this data in against
            date_format: the format the dates are in in the Posts and Commments
        """

        mezzanine_user = options.get("mezzanine_user")
        site = Site.objects.get_current()
        
        # set up the user to import under
        # and do some final checks in order to make sure it's legit
        if mezzanine_user is None:
            raise CommandError("No Mezzanine user has been specified")
        try:
            mezzanine_user = User.objects.get(username=mezzanine_user)
        except User.DoesNotExist: 
            raise CommandError("Invalid Mezzanine user: %s" % mezzanine_user)
        
        # now we try and import the blog
        self.handle_import(options)
                    
        # now process all the data in
        for entry in self.posts:
            print "Importing post titled: %s" % entry["title"]
            post, created = BlogPost.objects.get_or_create(
                user=mezzanine_user, title=entry["title"],
                content=entry["content"], 
                status=CONTENT_STATUS_PUBLISHED,
                publish_date=entry["publication_date"])
                
            for tag in entry["tags"]:
                keyword, created = Keyword.objects.get_or_create(title=tag)
                post.keywords.add(keyword)
            post.set_searchable_keywords()
            
            for comment in entry["comments"]:
                print "Importing comment by: %s" % comment["name"]
                thecomment, created = Comment.objects.get_or_create(
                    blog_post = post,
                    name = comment["name"],
                    email = comment["email"],
                    body = comment["body"],
                    website = comment["website"],
                    time_created = comment["time_created"] )
                
                post.comments.add(thecomment)

    def handle_import(self, options):
        """
        Should be overridden by subclasses - Performs the conversion from 
        the originating data source into the lists of posts and comments 
        ready for processing.
        """
        raise NotImplementedError
