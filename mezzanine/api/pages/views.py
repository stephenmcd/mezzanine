from rest_framework import generics
from mezzanine.pages.models import Page, RichTextPage
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from .serializers import PageSerializer, RichTextPageSerializer
from .filters import PageFilter


class PagesAPIView(generics.ListAPIView):
    queryset = Page.objects.all().filter(status=CONTENT_STATUS_PUBLISHED)
    serializer_class = PageSerializer
    filter_class = PageFilter


class RichTextPageAPIView(generics.ListAPIView):
    queryset = RichTextPage.objects.all()
    serializer_class = RichTextPageSerializer
