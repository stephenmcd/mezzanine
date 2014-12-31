import django_filters
from mezzanine.pages.models import Page


class PageFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(name='id', lookup_type='exact')
    title = django_filters.CharFilter(name='title', lookup_type='contains')
    name = django_filters.CharFilter(name='slug', lookup_type='exact')

    class Meta:
        model = Page
        fields = ['id', 'name', 'title', 'parent']
