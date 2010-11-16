from datetime import datetime, timedelta
from time import mktime, strftime, strptime, timezone
from xml.dom.minidom import parse, parseString

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.core.models import Keyword

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

class EmptyPostError(Error):
    """
    Exception raised in the case where a comment is being attempted to be
    added to an post that has not been specified
    """
    def __str__(self):
        return "Attempted to add a comment to no post"


class Importer(object):
    """
    Used to manage the importation of blog posts from a supported type
    into the Mezzanine format.
    """
    
    def __init__ (self, **kwargs):
        self.posts = []
        self.__dict__.update(kwargs)
        
        
    def add_post(self, title=None, author=None, pub_date=None, tags=None,
        content=None, comments=None):
        """
        Adds a post to the post list ready for processing
        
        Attributes:
            pub_date is assumed to be a datetime struct
        """
        if not comments:
            comments = []
        
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
        if not post:
            raise (EmptyPostError)
        else:
           post["comments"].append({
            "name": name,
            "email": email,
            "time_created": pub_date,
            "website": website,
            "body": body})
            
    def process(self, mezzanine_user=None):
        """
        Processes the converted data into the Mezzanine database correctly
        
        Attributes:
            mezzanine_user: the user to put this data in against
            date_format: the format the dates are in in the Posts and Commments
        """

        from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

        site = Site.objects.get_current()
        
        # set up the user to import under
        # and do some final checks in order to make sure it's legit
        if mezzanine_user is not None:
            try:
                mezzanine_user = User.objects.get(username=mezzanine_user)
            except User.DoesNotExist: 
                raise CommandError("Mezzanine user %s is not in the system" % mezzanine_user)
        else:
            if self.mezzanine_user:
                mezzanine_user = self.mezzanine_user
                try:
                    mezzanine_user = User.objects.get(username=mezzanine_user)
                except User.DoesNotExist: 
                    raise CommandError("Mezzanine user %s is not in the system" % mezzanine_user)
            else:
                raise CommandError("No user has been specified")
                    
        # now process all the data in
        for entry in self.posts:
            print "Imported %s" % entry["title"]
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
                print "Importing comment %s" % comment["name"]
                thecomment, created = Comment.objects.get_or_create(
                    blog_post = post,
                    name = comment["name"],
                    email = comment["email"],
                    body = comment["body"],
                    website = comment["website"],
                    time_created = comment["time_created"] )
                
                post.comments.add(thecomment)

                
    def convert(self):
        """
        does the conversion of the originating data source into the interim
        format ready for processing
        """
        raise NotImplementedError


        
class Wordpress(Importer):
    """
    Implements a Wordpress importer.  Takes a file path or a URL in order
    to point to the Wordpress Extended RSS file
    """

    def get_text(self, xml, element, nodetype):
        """
        Gets the element's text value from the xml object provided, adapted from
        minidom examples
        """
        rc = []
        for node in xml.getElementsByTagName(element)[0].childNodes:
            if node.nodeType == nodetype:
                rc.append(node.data)
        return "".join(rc)

           
    def convert(self):    
        """
        Gets the posts from either the provided URL or else
        from the path if it is local and then formats them back into the standard
        style ready for importation into Mezzanine. 
        """
    
        url = self.url

        try:
            import feedparser
        except ImportError:
            raise CommndError("You need to downlod feedparser - try easy_install feedparser")

        feed = feedparser.parse(url)

        # we use the minidom parser as well because feedparser won't interpret
        # WXR comments correctly and ends up munging them. Lightweight DOM parser is
        # used simply to pull the comments when we get to them. If someone wants
        # to rewrite this please do.
        xml = parse(url)
        xmlitems = xml.getElementsByTagName("item")

        total_posts = len(feed["entries"])
	
        print "Importing %s POSTS from Wordpress RSS2.0 feed at %s" % (total_posts, url)


        #i = 0 #counter for number of posts processed
        
        post_list = []
        
        for (i, entry) in enumerate(feed["entries"]):

            print "Processing post: %s/%s \n%s" % (i+1, total_posts, entry.title)
            
            # get a pointer to the right position in the minidom as well.
            xmlitem = xmlitems[i]
            i = i + 1
            
            title = entry.title
            content = entry.content[0]["value"]
            content = "<p>".join([content.replace("\n\n", "</p><p>"), "</p>"])

            # get the time struct of the published date if possible and the 
            # updated date if we can"t.
            try:
                pd = entry.published_parsed
            except AttributeError, err:
                pd = entry.updated_parsed
                
            published_date = datetime.fromtimestamp(mktime(pd)) - timedelta(seconds = timezone)
            
            tags = [tag.term for tag in entry.tags if tag.scheme !="category"]
            #tags have a tendency to not be unique in WP for some reason so
            # set the list so we have unique
            tags = list(set(tags))

            comments_list = []

            # create the temporary post object and append to the post_list
            
            post = self.add_post(
                title = title,
                content = content,
                pub_date = published_date,
                tags = tags)

            # get the comments from the xml doc.
            for comment in xmlitem.getElementsByTagName("wp:comment"):

           
                author_name = self.get_text(comment, "wp:comment_author", comment.CDATA_SECTION_NODE)
                email = self.get_text(comment, "wp:comment_author_email", comment.TEXT_NODE)
                website = ""
                if self.get_text(comment, "wp:comment_author_url", comment.TEXT_NODE):
                    website = self.get_text(comment, "wp:comment_author_url", comment.TEXT_NODE)
                body = self.get_text(comment, "wp:comment_content", comment.CDATA_SECTION_NODE)


                #use the GMT date (closest to UTC we'll end up with so this will
                # make it relatively timezone fine format is YYYY-MM-DD HH:MM:SS
                comment_date = datetime.strptime(
                    self.get_text(comment, "wp:comment_date_gmt", comment.TEXT_NODE),
                    "%Y-%m-%d %H:%M:%S" ) - timedelta(seconds = timezone)
                
                # add the comment as a dict to the end of the comments list
                self.add_comment(
                    post = post,
                    name = author_name,
                    email = email,
                    body = body,
                    website = website,
                    pub_date = comment_date)
                
class Blogger(Importer):
    """
    Implements a Blogger importer. Takes a blogger ID in order to be able to
    determine which blog it should point to and harvest the XML from
    """   
    gdata_url = "http://code.google.com/p/gdata-python-client/" 
    
        
    
    def convert(self):
        """
        Gets posts from blogger and then formats them back into the standard
        style ready for importation into Mezzanine.
        """

        blog_id = self.blog_id
        server = "www.blogger.com"
            
        try:
            from gdata import service
            import gdata
            import atom
        except ImportError:
            raise CommandError("You need to download the gdata python client module from %s to import blogger" % self.gdata_url)
        
        blogger = service.GDataService()
        blogger.service = "blogger"
        blogger.server = server
        query = service.Query()
        try:
            query.feed = "/feeds/" + blog_id + "/posts/full"
        except TypeError:
            raise CommandError("You have not supplied a blog id for blogger")
        query.max_results = 500
	
        try:
            feed = blogger.Get(query.ToUri())
        except gdata.service.RequestError, err:

            message = "There was a service error. The response was: %(status)s %(reason)s - %(body)s" % err.message
            raise FeedURLError(message, blogger.server + query.feed, err.message["status"])
            return
            
        total_posts = len(feed.entry)
	
        print "Importing %s POSTS from blogger atom feed at %s" % (total_posts, query.feed)
        
        post_list = []
        
        for (i, entry) in enumerate(feed.entry):
     
            # this basically gets the unique post id from the URL to itself. Pulls
            # the id off the end.
            post_id = entry.GetSelfLink().href.split("/")[-1]

            print "Processing post: %s/%s \n %s" % (i, total_posts, entry.title.text)
            
            title = entry.title.text
            content = entry.content.text
            #this strips off the time zone info off the end as we want UTC
            published_date = datetime.strptime(entry.published.text[:-6], 
                    "%Y-%m-%dT%H:%M:%S.%f") - timedelta(seconds = timezone)
            
            # get the tags
            tags = [tag.term for tag in entry.category]
            
            #TODO - issues with content not generating correct <P> tags
            

            post = self.add_post(
                title = title,
                content = content,
                pub_date = published_date,
                tags = tags)
            
            # get the comments from the post feed and then add them to the post details
            comment_url = "/feeds/" + blog_id + "/" + post_id + "/comments/full?max-results=1000"
            comments = blogger.Get(comment_url)
            
            print "Comments %s" % len(comments.entry)
            
            for comment in comments.entry:
                email = comment.author[0].email.text
                author_name = comment.author[0].name.text
                #this strips off the time zone info off the end as we want UTC
                comment_date = datetime.strptime(comment.published.text[:-6], 
                    "%Y-%m-%dT%H:%M:%S.%f") - timedelta(seconds = timezone)
                website = ""
                if comment.author[0].uri:
                    website = comment.author[0].uri.text
                body = comment.content.text
                
                # add the comment as a dict to the end of the comments list
                self.add_comment(
                    post = post,
                    name = author_name,
                    email = email,
                    body = body,
                    website = website,
                    pub_date = comment_date)
                

                    
    
