from django_filters import CharFilter
from django_filters import Filter
from django_filters import FilterSet

from mezzanine.blog.models import BlogPost


class BlogPostFilter(FilterSet):
    author = Filter(name='user__username', lookup_type='exact')
    title = CharFilter(name='title', lookup_type='contains')
    name = CharFilter(name='slug', lookup_type='exact')
    category = Filter(name='categories__slug')
    tag = Filter(name='keywords_string', lookup_type='contains')

    date = Filter(name='publish_date', lookup_type='lte')
    year = Filter(name='publish_date', lookup_type='year')
    month = Filter(name='publish_date', lookup_type='month')

    class Meta(object):
        model = BlogPost
        fields = ['name', 'title', 'tag', 'year', 'month',
                  'author', 'category']
