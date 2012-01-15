
from calendar import month_name
from collections import defaultdict

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.conf import settings
from mezzanine.generic.models import AssignedKeyword, Keyword
from mezzanine.generic.utils import handle_comments
from mezzanine.pages.models import RichTextPage
from mezzanine.template.loader import select_template
from mezzanine.utils.views import paginate


def blog_page():
    """
    Return the Blog page from the pages app.
    """
    try:
        return RichTextPage.objects.get(slug=settings.BLOG_SLUG)
    except RichTextPage.DoesNotExist:
        return None


def blog_post_list(request, tag=None, year=None, month=None, username=None,
                   category=None, template="blog/blog_post_list.html"):
    """
    Display a list of blog posts that are filtered by tag, year, month,
    author or category. Custom templates are checked for using the name
    ``blog/blog_post_list_XXX.html`` where ``XXX`` is either the
    category slug or author's username if given.
    """
    settings.use_editable()
    templates = []
    blog_posts = BlogPost.objects.published(for_user=request.user)
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        blog_posts = blog_posts.filter(keywords__in=tag.assignments.all())
    if year is not None:
        blog_posts = blog_posts.filter(publish_date__year=year)
        if month is not None:
            blog_posts = blog_posts.filter(publish_date__month=month)
            month = month_name[int(month)]
    if category is not None:
        category = get_object_or_404(BlogCategory, slug=category)
        blog_posts = blog_posts.filter(categories=category)
        templates.append(u"blog/blog_post_list_%s.html" % category.slug)
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        blog_posts = blog_posts.filter(user=author)
        templates.append(u"blog/blog_post_list_%s.html" % username)
    # Create dicts mapping blog post IDs to lists of categories and
    # keywords, and assign these to each blog post, to avoid querying
    # the database inside the template loop for posts.
    blog_posts = list(blog_posts.select_related("user"))
    categories = defaultdict(list)
    if blog_posts:
        ids = ",".join([str(p.id) for p in blog_posts])
        for cat in BlogCategory.objects.raw(
            "SELECT * FROM blog_blogcategory "
            "JOIN blog_blogpost_categories "
            "ON blog_blogcategory.id = blogcategory_id "
            "WHERE blogpost_id IN (%s)" % ids):
            categories[cat.blogpost_id].append(cat)
    keywords = defaultdict(list)
    blogpost_type = ContentType.objects.get(app_label="blog", model="blogpost")
    assigned = AssignedKeyword.objects.filter(blogpost__in=blog_posts,
                          content_type=blogpost_type).select_related("keyword")
    for a in assigned:
        keywords[a.object_pk].append(a.keyword)
    for i, post in enumerate(blog_posts):
        setattr(blog_posts[i], "category_list", categories[post.id])
        setattr(blog_posts[i], "keyword_list", keywords[post.id])
    blog_posts = paginate(blog_posts,
                          request.GET.get("page", 1),
                          settings.BLOG_POST_PER_PAGE,
                          settings.BLOG_POST_MAX_PAGING_LINKS)
    context = {"blog_page": blog_page(), "blog_posts": blog_posts,
               "year": year, "month": month, "tag": tag,
               "category": category, "author": author}
    templates.append(template)
    request_context = RequestContext(request, context)
    t = select_template(templates, request_context)
    return HttpResponse(t.render(request_context))


def blog_post_detail(request, slug, template="blog/blog_post_detail.html",
                             year=None, month=None,):
    """
    Display a blog post and handle comment submission. Custom
    templates are checked for using the name
    ``blog/blog_post_detail_XXX.html`` where ``XXX`` is the blog
    posts's slug.
    """
    blog_posts = BlogPost.objects.published(for_user=request.user)
    blog_post = get_object_or_404(blog_posts, slug=slug)
    # Handle comments
    comment_parts = handle_comments(blog_post, request)
    posted_comment_form, unposted_comment_form, response = comment_parts
    if response is not None:
        return response
    context = {"blog_page": blog_page(), "blog_post": blog_post,
               "posted_comment_form": posted_comment_form,
               "unposted_comment_form": unposted_comment_form}
    templates = [u"blog/blog_post_detail_%s.html" % slug, template]
    request_context = RequestContext(request, context)
    t = select_template(templates, request_context)
    return HttpResponse(t.render(request_context))
