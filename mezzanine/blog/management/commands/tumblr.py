from urllib import urlopen
from urlparse import urlparse

from datetime import datetime
from time import strftime, strptime

from importer import BlogPostImport, BlogCommentImport
from importer import FeedURLError

from django.utils.simplejson import loads

# Adapted from Stephen_mcd's original implementation and brought back into
# line with the more comprehensive set up being used now.


def GetTumblrPosts(tumblr_user=""):

    json_url = "http://%s.tumblr.com/api/read/json" % tumblr_user
    
    try:
        response = urlopen(json_url)
        if response.code == 404:
            raise FeedURLError("Invalid Tumblr user", json_url, "404")
        elif response.code == 503:
            raise FeedURLError("Tumblr API currently unavailable", json_url, "503")
        elif response.code != 200:
            raise IOError("General HTTP error", json_url, response.code)
    except IOError, e:
        raise FeedURLError("Error communicating with Tumblr API", json_url, "%s" % e)

    start = "var tumblr_api_read ="
    json = loads(response.read().split(start, 1)[1].strip().rstrip(";"))

    total_posts = len(json["posts"])
    
    print "Importing %s tubmlr posts from %s" % (total_posts, json_url)
    
    for entry in json["posts"]:
        print "type: %s" % entry["type"]

        #TODO: finish off rewriting the tumblr stuff entirely.


