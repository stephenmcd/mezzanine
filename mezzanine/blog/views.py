
from calendar import month_name
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template

from mezzanine.blog.forms import CommentForm
from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.conf import settings
from mezzanine.core.models import Keyword
from mezzanine.pages.models import ContentPage
from mezzanine.utils import paginate


def blog_page():
    """
    Return the Blog page from the pages app.
    """
    try:
        return ContentPage.objects.get(slug=settings.BLOG_SLUG)
    except ContentPage.DoesNotExist:
        return None

def blog_post_list(request, tag=None, year=None, month=None, username=None,
    category=None, template="blog/blog_post_list.html"):
    """
    Display a list of blog posts.
    """
    settings.use_editable()
    blog_posts = BlogPost.objects.published(for_user=request.user)
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        blog_posts = blog_posts.filter(keywords=tag)
    if year is not None:
        blog_posts = blog_posts.filter(publish_date__year=year)
        if month is not None:
            blog_posts = blog_posts.filter(publish_date__month=month)
            month = month_name[int(month)]
    if category is not None:
        category = get_object_or_404(BlogCategory, slug=category)
        blog_posts = blog_posts.filter(category=category)
    user = None
    if username is not None:
        user = get_object_or_404(User, username=username)
        blog_posts = blog_posts.filter(user=user)
    blog_posts = paginate(blog_posts, request.GET.get("page", 1),
        settings.BLOG_POST_PER_PAGE,
        settings.BLOG_POST_MAX_PAGING_LINKS)
    context = {"blog_posts": blog_posts, "year": year, "month": month, 
        "tag": tag, "category": category, "user": user, 
        "use_disqus": bool(settings.COMMENTS_DISQUS_SHORTNAME), 
        "blog_page": blog_page()}
    return render_to_response(template, context, RequestContext(request))


def blog_post_detail(request, slug, template="blog/blog_post_detail.html"):
    """
    Display a blog post.
    """
    # Create two comment forms - one with posted data and errors that will be
    # matched to the form submitted via comment_id, and an empty one for all
    # other instances.
    commenter_cookie_prefix = "mezzanine-blog-"
    commenter_cookie_fields = ("name", "email", "website")
    initial_comment_data = dict([(f, request.COOKIES.get(
        commenter_cookie_prefix + f, "")) for f in commenter_cookie_fields])
    blog_posts = BlogPost.objects.published(for_user=request.user)
    blog_post = get_object_or_404(blog_posts, slug=slug)
    posted_comment_form = CommentForm(request.POST or None,
        initial=initial_comment_data)
    unposted_comment_form = CommentForm(initial=initial_comment_data)
    if request.method == "POST" and posted_comment_form.is_valid():
        comment = posted_comment_form.save(commit=False)
        comment.blog_post = blog_post
        comment.by_author = (request.user == blog_post.user and
            request.user.is_authenticated)
        comment.ip_address = request.META.get("HTTP_X_FORWARDED_FOR",
            request.META["REMOTE_ADDR"])
        comment.replied_to_id = request.POST.get("replied_to")
        comment.save()
        response = HttpResponseRedirect(comment.get_absolute_url())
        # Store commenter's details in a cookie for 90 days.
        expires = datetime.strftime(datetime.utcnow() +
            timedelta(seconds=90 * 24 * 60 * 60), "%a, %d-%b-%Y %H:%M:%S GMT")
        for field in commenter_cookie_fields:
            response.set_cookie(commenter_cookie_prefix + field,
                request.POST.get(field, ""), expires=expires)
        return response
    settings.use_editable()
    context = {"blog_post": blog_post, "blog_page": blog_page(), 
        "use_disqus": bool(settings.COMMENTS_DISQUS_SHORTNAME), 
        "posted_comment_form": posted_comment_form, 
        "unposted_comment_form": unposted_comment_form}
    t = select_template(["blog/%s.html" % slug, template])
    return HttpResponse(t.render(RequestContext(request, context)))
