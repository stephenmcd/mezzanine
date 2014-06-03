from rest_framework import generics
from pages.models import Page
from .serializers import PageSerializer

class PagesAPIView(generics.ListAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer