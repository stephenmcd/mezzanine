from rest_framework import generics
from mezzanine.pages.models import Page
from .serializers import  PageSerializer


class PagesAPIView(generics.ListAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
