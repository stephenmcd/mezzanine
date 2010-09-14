from datetime import datetime, timedelta
from time import timezone

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.core.models import Keyword
from mezzanine.settings import CONTENT_STATUS_PUBLISHED

from django.core.management.base import BaseCommand, CommandError

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
    
    
def Import(mezzanine_user='', posts_list=[], date_format=None):
    """
    Does the actual import process into Mezzanine
    
    Attributes:
        mezzanine_user: the user to import this against
        post_list: the list of posts to import in BlogPostImport objects
        date_format: the format the dates are in in the Posts and Commments
    """

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
            print "Importing %s" % comment.name
            thecomment, created = Comment.objects.get_or_create(
                blog_post = post,
                name = comment.name,
                email = comment.email,
                body = comment.body,
                website = comment.website,
                time_created = datetime.strptime(comment.time_created, date_format) - timedelta(seconds = timezone))
            
            post.comments.add(thecomment)

def TestImport():
    """
    Tests the import script
    """
    #ImportBlogger(mezzanine_user='fishera', blog_id='8183712382911359730')
    ImportBlogger(mezzanine_user='fishera', blog_id='')
