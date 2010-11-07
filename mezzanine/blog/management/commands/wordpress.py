from datetime import datetime
from time import strftime, strptime
from xml.dom.minidom import parse, parseString

import feedparser

from importer import BlogPostImport, BlogCommentImport

def get_text(xml, element, nodetype):
    """
    Gets the element's text value from the xml object provided, adapted from
    minidom examples
    """
    rc = []
    for node in xml.getElementsByTagName(element)[0].childNodes:
        if node.nodeType == nodetype:
            rc.append(node.data)
    return "".join(rc)

def get_wp_posts(url=""):
    """
    Gets the posts from either the provided URL or else
    from the path if it is local and then formats them back into the standard
    style ready for importation into Mezzanine. Returns a list of BlogPostImport
    objects
    """

    feed = feedparser.parse(url)

    # we use the minidom parser as well because feedparser won't interpret
    # WXR comments correctly and ends up munging them. Lightweight DOM parser is
    # used simply to pull the comments when we get to them. If someone wants
    # to rewrite this please do.
    xml = parse(url)
    xmlitems = xml.getElementsByTagName("item")

    total_posts = len(feed["entries"])
	
    print "Importing %s POSTS from Wordpress RSS2.0 feed at %s" % (total_posts, url)


    i = 0 #counter for number of posts processed
    
    post_list = []
    
    for entry in feed["entries"]:

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
            
        published_date = strftime("%c", pd)
        
        
        # get the tags
        tags = []
        for tag in entry.tags:
            if tag.scheme != "category":
                tags.append(tag.term)
             
        #tags have a tendency to not be unique in WP for some reason so
        # set the list so we have unique
        tags = list(set(tags))
        

        comments_list = []

        # get the comments from the xml doc.
        for comment in xmlitem.getElementsByTagName("wp:comment"):

       
            author_name = get_text(comment, "wp:comment_author", comment.CDATA_SECTION_NODE)
            email = get_text(comment, "wp:comment_author_email", comment.TEXT_NODE)
            website = ""
            if get_text(comment, "wp:comment_author_url", comment.TEXT_NODE):
                website = get_text(comment, "wp:comment_author_url", comment.TEXT_NODE)
            body = get_text(comment, "wp:comment_content", comment.CDATA_SECTION_NODE)


            #use the GMT date (closest to UTC we'll end up with so this will
            # make it relatively timezone fine format is YYYY-MM-DD HH:MM:SS
            comment_date = strptime(
                get_text(comment, "wp:comment_date_gmt", comment.TEXT_NODE),
                "%Y-%m-%d %H:%M:%S" )
            comment_date = strftime("%c", comment_date)
            #print "date: %s" % strftime("%c", comment_date)
            
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
            
    return (post_list, url)
