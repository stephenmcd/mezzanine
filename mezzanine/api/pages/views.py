from rest_framework import viewsets
from mezzanine.pages.models import Page

from .serializers import PageSerializer
from .filters import PageFilter


class PagesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.published()
    serializer_class = PageSerializer
    filter_class = PageFilter
