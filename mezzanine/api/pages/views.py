from rest_framework import generics
from mezzanine.pages.models import Page
from mezzanine.pages.models import RichTextPage

from .serializers import PageSerializer
from .serializers import RichTextPageSerializer
from .filters import PageFilter


class PagesAPIView(generics.ListAPIView):
    queryset = Page.objects.published()
    serializer_class = PageSerializer
    filter_class = PageFilter


class RichTextPageAPIView(generics.ListAPIView):
    queryset = RichTextPage.objects.published()
    serializer_class = RichTextPageSerializer
