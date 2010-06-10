
from collections import defaultdict
from datetime import datetime, timedelta
from time import timezone
from urllib import urlopen, urlencode

from django import template
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.simplejson import loads

from mezzanine import settings as blog_settings
from mezzanine.blog.forms import BlogPostForm
from mezzanine.blog.models import Comment, BlogPost
from mezzanine.core.models import Keyword
from mezzanine.core.templatetags.mezzanine_tags import register_as_tag


register = template.Library()


@register.simple_tag
def gravatar_url(email_hash, size=32):
    """
    Return the full URL for a Gravatar given an email hash.
    """
    return "http://www.gravatar.com/avatar/%s?s=%s" % (email_hash, size)

thread_template = "blog/includes/comments_thread.html"
@register.inclusion_tag(thread_template, takes_context=True)
def blog_comments_for(context, parent):
    """
    Return a list of child comments for the given parent, storing all 
    comments in a dict in the context when first called using parents as keys 
    for retrieval on subsequent recursive calls from the comments template.
    """
    if "blog_comments" not in context:
        comments = defaultdict(list)
        for comment in parent.comments.visible():
            comments[comment.replied_to_id].append(comment)
        context["blog_comments"] = comments
        parent = None
    else:
        parent = parent.id
    context.update({
        "comments_thread": context["blog_comments"].get(parent, []),
        "no_comments": parent is None and not comments,
        "comments_default_approved": blog_settings.COMMENTS_DEFAULT_APPROVED,
        "replied_to": int(context["request"].POST.get("replied_to", 0)),
    })
    return context

@register_as_tag(register)
def blog_months(*args):
    """
    Put a list of dates for blog posts into the template context.
    """
    return BlogPost.objects.published().dates("publish_date", "month", 
        order="DESC")

@register_as_tag(register)
def blog_tags(*args):
    """
    Put a list of tags (keywords) for blog posts into the template context.
    """
    tags = Keyword.objects.filter(blogpost__isnull=False).annotate(
        post_count=Count("blogpost"))
    if not tags:
        return []
    counts = [tag.post_count for tag in tags]
    min_count, max_count = min(counts), max(counts)
    sizes = blog_settings.TAG_CLOUD_SIZES
    step = (max_count - min_count) / (sizes - 1)
    if step == 0:
        steps = [sizes / 2]
    else:
        steps = range(min_count, max_count, step)[:sizes]
    for tag in tags:
        c = tag.post_count
        diff = min([(abs(s - c), (s - c)) for s in steps])[1]
        tag.weight = steps.index(c + diff) + 1
    return tags

@register_as_tag(register)
def blog_authors(*args):
    """
    Put a list of authors (users) for blog posts into the template context.
    """
    blog_posts = BlogPost.objects.published()
    return User.objects.filter(blog_posts__in=blog_posts).distinct()

@register_as_tag(register)
def quick_blog_form(*args):
    """
    Puts the quick blog form into the admin dashboard.
    """
    return BlogPostForm()

DISQUS_FORUM_ID = None
recent_comments_template = "admin/includes/recent_comments.html"
@register.inclusion_tag(recent_comments_template, takes_context=True)
def recent_comments(context):
    """
    If the COMMENTS_DISQUS_SHORTNAME and COMMENTS_DISQUS_KEY settings have been 
    set, pull the latest comments in from the Disqus API, using the global 
    DISQUS_FORUM_ID so that this lookup occurs only once, transforming each 
    comment into a dict that looks like the built-in comments model. If these 
    are not set then use the built-in comments model.
    """

    global DISQUS_FORUM_ID
    disqus_key = blog_settings.COMMENTS_DISQUS_KEY
    disqus_shortname = blog_settings.COMMENTS_DISQUS_SHORTNAME
    latest = blog_settings.COMMENTS_NUM_LATEST
    context["comments"] = []
    post_from_comment = lambda comment: int(comment["thread"]["identifier"][0])

    def disqus_api(method, **args):
        """
        Make a call to the Disqus API, parsing the JSON data into Python.
        """
        args.update({"user_api_key": disqus_key, "api_version": "1.1"})
        url = "http://disqus.com/api/%s/?%s" % (method, urlencode(args))
        response = loads(urlopen(url).read())
        return response["message"] if response["succeeded"] else []
    
    if disqus_shortname and disqus_key:
        if DISQUS_FORUM_ID is None:
            forums = disqus_api("get_forum_list")
            for forum in forums:
                if forum["shortname"] == disqus_shortname:
                    DISQUS_FORUM_ID = forum["id"]
        if DISQUS_FORUM_ID is not None:
            comments = disqus_api("get_forum_posts", forum_id=DISQUS_FORUM_ID, 
                limit=latest, exclude="spam,killed")
            posts = BlogPost.objects.in_bulk(map(post_from_comment, comments))
            for comment in comments:
                try:
                    blog_post = posts[post_from_comment(comment)]
                    comment_url = "%s#comment-%s" % (
                        post.get_absolute_url(), comment["id"])
                except KeyError:
                    blog_post = None
                    comment_url = ""
                context["comments"].append({
                    "name": comment["author"]["display_name"],
                    "email": comment["author"]["email"],
                    "email_hash": comment["author"]["email_hash"],
                    "body": comment["message"],
                    "time_created": datetime.strptime(comment["created_at"], 
                        "%Y-%m-%dT%H:%M") - timedelta(seconds=timezone),
                    "get_absolute_url": comment_url,
                    "post": blog_post,
                })
    else:
        context["comments"] = Comment.objects.all().order_by("-id")[:latest]
    return context

