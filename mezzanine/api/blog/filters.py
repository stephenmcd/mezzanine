import django_filters
from mezzanine.blog.models import BlogPost


class BlogPostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(name='title', lookup_type='contains')
    name = django_filters.CharFilter(name='slug', lookup_type='exact')
    category = django_filters.Filter(name='categories__slug')
    author = django_filters.Filter(name='user__username', lookup_type='exact')
    tag = django_filters.Filter(name='keywords_string', lookup_type='contains')

    year = django_filters.Filter(name='publish_date', lookup_type='year')
    month = django_filters.Filter(name='publish_date', lookup_type='month')

    class Meta:
        model = BlogPost
        fields = ['name', 'title', 'tag', 'year', 'month',
                  'author', 'category']
