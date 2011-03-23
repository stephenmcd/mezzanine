
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Count

from mezzanine.conf import settings
from mezzanine.blog.forms import BlogPostForm
from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.core.models import Keyword
from mezzanine import template


register = template.Library()


@register.as_tag
def blog_months(*args):
    """
    Put a list of dates for blog posts into the template context.
    """
    dates = BlogPost.objects.published().values_list("publish_date", flat=True)
    date_dicts = [{"date": datetime(d.year, d.month, 1)} for d in dates]
    month_dicts = []
    for date_dict in date_dicts:
        if date_dict not in month_dicts:
            month_dicts.append(date_dict)
    for i, date_dict in enumerate(month_dicts):
        month_dicts[i]["post_count"] = date_dicts.count(date_dict)
    return month_dicts


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
    return list(User.objects.filter(blogposts__in=blog_posts).annotate(post_count=Count("blogposts")))


@register.as_tag
def blog_recent_posts(limit=5):
    """
    Put a list of recently published blog posts into the template context.
    """
    return list(BlogPost.objects.published()[:limit])


@register.inclusion_tag("admin/includes/quick_blog.html", takes_context=True)
def quick_blog(context):
    """
    Admin dashboard tag for the quick blog form.
    """
    context["form"] = BlogPostForm()
    return context
