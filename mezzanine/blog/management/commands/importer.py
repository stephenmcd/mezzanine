"""
 Importer module used to import blog posts and comments from a variety
 of alternative blog systems such as wordpress, blogger and tumblr
"""



from datetime import datetime, timedelta
from time import timezone

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.core.models import Keyword

from django.core.management.base import BaseCommand, CommandError

from optparse import make_option




__VERSION__ = "0.8.1"

class Command(BaseCommand):
    """
    Import Blog Posts into mezzanine from a variety of different sources
    """
    
    option_list = BaseCommand.option_list + (
        make_option('-t', '--blogtype', dest="blogtype", 
            help="Type of blog to parse. [blogger, wordpress, tumblr]"),
        make_option('-b', '--blogger', dest='bloggerid',
            help="Blogger Blog ID from blogger dashboard"),
        make_option('-f', '--filepath', dest='filepath',
            help="Path to import file"),
        make_option('-u', '--url', dest='importurl',
            help="URL to import file"),
        make_option('-r', '--tumblr', dest='tumblruser',
            help="Tumblr user id"),
        make_option('-m', '--mezzanine-user', dest='mezzuser',
            help="Mezzanine username to assign the imported blog posts into"),
    )
    
    
    def handle(self, *args, **options):
    
        blogtype = options["blogtype"]   
        mezzuser = options["mezzuser"]
        
        if mezzuser==None:
            raise CommandError("Please ensure a mezzanine user is specified")
    
        if (blogtype=="wordpress"):
            if options['filepath']:
                ImportWordPress(mezzanine_user=mezzuser, path=options['filepath'])
            elif options['importurl']:
                ImportWordPress(mezzanine_user=mezzuser, url=options['importurl'])
            else:
                raise CommandError("Please supply a file path or url to the WP WRX file")
        
        elif (blogtype=="blogger"):
            if options['bloggerid']:
                ImportBlogger(mezzaning_user=mezzuser, blog_id=options['bloggerid'])
            else:
                raise CommandError("Please supply a blogger post id")
            
        elif (blogtype=="tumblr"):
            if options['tumblruser']:
                ImportTumblr(mezzanine_user=mezzuser, tumblr_user=options['tumblruser'])
            else:
                raise CommandError("Please specify a tumblr user account id")
        else:
            raise CommandError("Please specifiy a blog type for import")
        
    
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
    
    def get_version(self):
        return "v%s" % __VERSION__

class Error(Exception):
    """
    Base class for errors in this module
    """
    
    pass
    
class EmptyFeedError(Error):
    """
    Exception raised for the case where a valid feed has returned no posts
    
    Attributes:
        msg: explanation of the error
        url: the feed url that was called
    """
    def __init__(self, msg, url):
        self.msg = msg
        self.url = url

class FeedURLError(Error):
    """
    Exception raised in the case where the URL that is hit for the feed doesn't
    return correctly at all
    
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
    
    

class BlogPostImport():
    """
    An intermediate object used to store blog data in a consistent manner before
    passing into the Mezzanine data side for storage.
    """
    
    def __init__ (self, title=None, author=None, pub_date=None, 
                  tags=None, content=None, comments=[]):
                  
        self.title = title
        #self.author = author
        self.publication_date = pub_date
        self.tags = tags
        self.content = content
        self.comments = comments
        
class BlogCommentImport():
    """
    An intermediate object used to store blog comments in a consistent manner
    before passing into the Mezzanine side for storage.
    """
    
    def __init__(self, name=None, email=None, body=None, 
                website=None, pub_date=None):
                
        self.name = name
        self.email = email
        self.time_created = pub_date
        self.website = website
        self.body = body
        

def ImportBlogger(mezzanine_user='', blog_id=''):
    """
    Does the set up and import of a blogger blog.
    Takes a mezzanine user to import the blogs as and the
    blog id (see docs) of the blog to import
    """
    
    import blogger

    try:
        posts_list, feed_url = blogger.GetBloggerPosts(blog_id)
    except FeedURLError, err:
        raise CommandError(err)

    if not posts_list:
        raise EmptyFeedError(msg='Blogger returned no data in the feed', url=feed_url)
    else:
        Import(mezzanine_user=mezzanine_user, posts_list=posts_list, 
                date_format = "%Y-%m-%dT%H:%M:%S.%f")

def ImportWordPress(mezzanine_user='', path='', url=''):
    """
    Does the set up and importing of the wordpress blog.
    Takes a mezzanine user as well as either a path or url to the WXR file
    """ 
    
    import wordpress
    
    if (url == '' and path !=''):
        url = path
    
    try:
        posts_list, feed_url = wordpress.GetWPPosts(url)
    except FeedURLError, err:
        raise CommandError(err)
    
    if not posts_list:
        raise EmptyFeedError(msg='WP returned no data in the feed', url=feed_url)
    else:
        #pass
        Import(mezzanine_user=mezzanine_user, posts_list=posts_list, 
                date_format = "%c")
        

def ImportTumblr(mezzanine_user='', tumblr_user=''):
    """
    Does the set up and importing of the tumblr blog.
    Takes a mezzanine user as well as the tumblr user as inputs
    """
    
    import tumblr
    
    try:
        posts_list, feed_url = tumblr.GetTumblrPosts(tumblr_user)
    except FeedURLError, err:
        raise CommandError(err)
        
    if not posts_list:
        raise EmptyFeedError(msg='Tumblr returned no data in the feed', url=feed_url)
    else:
        #pass
        Import(mezzanine_user=mezzanine_user, posts_list=posts_list, 
                date_format = "%c")
                
    
def Import(mezzanine_user='', posts_list=[], date_format=None):
    """
    Does the actual import process into Mezzanine
    
    Attributes:
        mezzanine_user: the user to import this against
        post_list: the list of posts to import in BlogPostImport objects
        date_format: the format the dates are in in the Posts and Commments
    """

    from mezzanine.core.models.displayable import CONTENT_STATUS_PUBLISHED

    site = Site.objects.get_current()
    
    # set up the user to import under
    if mezzanine_user is not None:
        try:
            mezzanine_user = User.objects.get(username=mezzanine_user)
        except User.DoesNotExist: 
            print 'User not valid'
            return
    
    for entry in posts_list:
        print 'Imported %s' % entry.title
        post, created = BlogPost.objects.get_or_create(
            user=mezzanine_user, title=entry.title,
            content=entry.content, 
            status=CONTENT_STATUS_PUBLISHED,
            publish_date=datetime.strptime(entry.publication_date, date_format) - timedelta(seconds = timezone))
        for tag in entry.tags:
            keyword, created = Keyword.objects.get_or_create(title=tag)
            post.keywords.add(keyword)
        post.set_searchable_keywords()
        
        
        for comment in entry.comments:
            print "Importing comment %s" % comment.name
            thecomment, created = Comment.objects.get_or_create(
                blog_post = post,
                name = comment.name,
                email = comment.email,
                body = comment.body,
                website = comment.website,
                time_created = datetime.strptime(comment.time_created, date_format) - timedelta(seconds = timezone))
            
            post.comments.add(thecomment)


