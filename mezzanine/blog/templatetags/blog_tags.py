
from collections import defaultdict
from datetime import datetime, timedelta
from time import timezone
from urllib import urlopen, urlencode

from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.simplejson import loads

from mezzanine.conf import settings
from mezzanine.blog.forms import BlogPostForm
from mezzanine.blog.models import BlogPost, BlogCategory, Comment
from mezzanine.core.models import Keyword
from mezzanine import template


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
    try:
        replied_to = int(context["request"].POST["replied_to"])
    except KeyError:
        replied_to = 0
    context.update({
        "comments_thread": context["blog_comments"].get(parent, []),
        "no_comments": parent is None and not comments,
        "replied_to": replied_to,
    })
    return context


@register.as_tag
def blog_months(*args):
    """
    Put a list of dates for blog posts into the template context.
    """
    months = []
    for month in BlogPost.objects.published().dates("publish_date", "month",
                                                    order="DESC"):
        if month not in months:
            months.append(month)
    return months


@register.as_tag
def blog_categories(*args):
    """
    Put a list of categories for blog posts into the template context.
    """
    posts = BlogPost.objects.published()
    return list(BlogCategory.objects.filter(blogposts__in=posts).distinct())


@register.as_tag
def blog_tags(*args):
    """
    Put a list of tags (keywords) for blog posts into the template context.
    """
    tags = Keyword.objects.filter(blogpost__isnull=False).annotate(
        post_count=Count("blogpost"))
    if not tags:
        return []
    settings.use_editable()
    counts = [tag.post_count for tag in tags]
    min_count, max_count = min(counts), max(counts)
    sizes = settings.TAG_CLOUD_SIZES
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


@register.as_tag
def blog_authors(*args):
    """
    Put a list of authors (users) for blog posts into the template context.
    """
    blog_posts = BlogPost.objects.published()
    return list(User.objects.filter(blogposts__in=blog_posts).distinct())

@register.as_tag
def get_recent_posts(limit):
    """
    Put a list of recently published blog posts into the template context.
    """
    return BlogPost.objects.published()[:limit]

@register.inclusion_tag("admin/includes/quick_blog.html", takes_context=True)
def quick_blog(context):
    """
    Admin dashboard tag for the quick blog form.
    """
    context["form"] = BlogPostForm()
    return context


DISQUS_FORUM_ID = None

@register.inclusion_tag("admin/includes/recent_comments.html", 
    takes_context=True)
def recent_comments(context):
    """
    If the ``COMMENTS_DISQUS_SHORTNAME`` and ``COMMENTS_DISQUS_KEY`` settings
    have been set, pull the latest comments in from the Disqus API, using the
    global ``DISQUS_FORUM_ID`` so that this lookup occurs only once,
    transforming each comment into a dict that looks like the built-in
    ``Comment`` model. If these are not set then use the built-in ``Comment``
    model.
    """

    global DISQUS_FORUM_ID
    settings = context["settings"]
    disqus_key = settings.COMMENTS_DISQUS_KEY
    disqus_shortname = settings.COMMENTS_DISQUS_SHORTNAME
    latest = settings.COMMENTS_NUM_LATEST
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
                except KeyError:
                    blog_post = None
                context["comments"].append({
                    "name": comment["author"]["display_name"],
                    "email": comment["author"]["email"],
                    "email_hash": comment["author"]["email_hash"],
                    "body": comment["message"],
                    "time_created": datetime.strptime(comment["created_at"],
                        "%Y-%m-%dT%H:%M") - timedelta(seconds=timezone),
                    "post": blog_post,
                })
    else:
        context["comments"] = Comment.objects.all().select_related(
            ).order_by("-id")[:latest]
    return context
