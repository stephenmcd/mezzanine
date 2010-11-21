
from datetime import datetime, timedelta
from optparse import make_option
from time import mktime, strftime, strptime, timezone

from django.core.management.base import CommandError

from mezzanine.blog.management.base import BaseImporterCommand


class Command(BaseImporterCommand):
    """
    Implements a Blogger importer. Takes a blogger ID in order to be able to
    determine which blog it should point to and harvest the XML from
    """   
    gdata_url = "http://code.google.com/p/gdata-python-client/" 
    
    option_list = BaseImporterCommand.option_list + (
        make_option("-b", "--blogger", dest="blog_id",
            help="Blogger Blog ID from blogger dashboard"),
    )
    
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
