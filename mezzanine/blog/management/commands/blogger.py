from datetime import datetime

from importer import BlogPostImport, BlogCommentImport
from importer import FeedURLError

gdata_url = "http://code.google.com/p/gdata-python-client/"

def get_blogger_posts(blog_id="", server="www.blogger.com"):
    """
    Gets posts from blogger and then formats them back into the standard
    style ready for importation into Mezzanine. Returns a list of BlogPostImport
    objects
    """

    try:
        from gdata import service
        import gdata
        import atom
    except ImportError:
        raise CommandError("You need to download the gdata python client module from %s to import blogger" % gdata_url)
    
    blogger = service.GDataService()
    blogger.service = "blogger"
    blogger.server = server
    query = service.Query()
    query.feed = "/feeds/" + blog_id + "/posts/full"
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
        published_date = entry.published.text[:-6]
        
        # get the tags
        tags = []
        for tag in entry.category:
            #print "tag: %s" % tag.term
            tags.append(tag.term)
        
        #TODO - issues with content not generating correct <P> tags
        
        
        
        # get the comments from the post feed and then add them to the post details
        comment_url = "/feeds/" + blog_id + "/" + post_id + "/comments/full?max-results=1000"
        comments = blogger.Get(comment_url)
        
        print "Comments %s" % len(comments.entry)
        
        comments_list = []   
        for comment in comments.entry:
            email = comment.author[0].email.text
            author_name = comment.author[0].name.text
            #this strips off the time zone info off the end as we want UTC
            comment_date = comment.published.text[:-6]
            website = ""
            if comment.author[0].uri:
                website = comment.author[0].uri.text
            body = comment.content.text
            
            # create a temp comment object and put in the comments list
            comments_list.append(BlogCommentImport(
                name = author_name,
                email = email,
                body = body,
                website = website,
                pub_date = comment_date))
            
            
        
        # create the temporary post object and append to the post_list
        post_list.append(BlogPostImport(
            title = title,
            content = content,
            pub_date = published_date,
            tags = tags,
            comments = comments_list))
            
    return (post_list, (blogger.server + query.ToUri()))
