
from calendar import month_name

from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template

from mezzanine.blog.forms import CommentForm
from mezzanine.blog.models import BlogPost
from mezzanine import settings as blog_settings


use_disqus = bool(blog_settings.COMMENTS_DISQUS_SHORTNAME)


def blog_post_list(request, tag=None, year=None, month=None, username=None, 
    template="blog/blog_post_list.html"):
    """
    Display a list of blog posts.
    """
    blog_posts = BlogPost.objects.published(for_user=request.user).annotate(
        num_comments=Count("comments"))
    if tag is not None:
        blog_posts = blog_posts.filter(keywords__value=tag)
    if year is not None:
        blog_posts = blog_posts.filter(publish_date__year=year) 
        if month is not None:
            blog_posts = blog_posts.filter(publish_date__month=month)
            month = month_name[int(month)]
    user = None
    if username is not None:
        user = get_object_or_404(User, username=username)
        blog_posts = blog_posts.filter(user=user)
    paginator = Paginator(blog_posts, blog_settings.BLOG_POST_PER_PAGE)
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    try:
        posts = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)
    page_range = posts.paginator.page_range
    max_links = blog_settings.BLOG_POST_MAX_PAGING_LINKS
    if len(page_range) > max_links:
        start = min(posts.paginator.num_pages - max_links, 
            max(0, blog_posts.number - (max_links / 2) - 1))
        page_range = page_range[start:start + max_links]
    context = {"posts": posts, "page_range": page_range, "tag": tag, 
        "year": year, "month": month, "user": user, "use_disqus": use_disqus}
    return render_to_response(template, context, RequestContext(request))

def blog_post_detail(request, slug, template="blog/blog_post_detail.html"):
    """
    Display a blog post.
    """
    # Create two comment forms - one with posted data and errors that will be 
    # matched to the form submitted via comment_id, and an empty one for all 
    # other instances.
    blog_post = get_object_or_404(
        BlogPost.objects.published(for_user=request.user), slug=slug)
    posted_comment_form = CommentForm(request.POST or None)
    unposted_comment_form = CommentForm()
    if request.method == "POST" and posted_comment_form.is_valid():
        comment = posted_comment_form.save(commit=False)
        comment.blog_post = blog_post
        comment.ip_address = request.META.get("HTTP_X_FORWARDED_FOR", 
	        request.META["REMOTE_ADDR"])
        comment.replied_to_id = request.POST.get("replied_to")
        comment.save()
        return HttpResponseRedirect(comment.get_absolute_url())
    context = {"blog_post": blog_post, "use_disqus": use_disqus, 
        "posted_comment_form": posted_comment_form, "unposted_comment_form": 
        unposted_comment_form}
    t = select_template(["blog/%s.html" % slug, template])
    return HttpResponse(t.render(RequestContext(request, context)))

