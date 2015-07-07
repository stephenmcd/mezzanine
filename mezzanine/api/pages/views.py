from rest_framework import filters
from rest_framework import viewsets
from mezzanine.pages.models import Page

from .serializers import PageSerializer


class PagesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.published()
    serializer_class = PageSerializer

    filter_backends = (filters.SearchFilter, )
    search_fields = ('^title', '=slug', '=id')
