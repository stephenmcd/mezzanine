from rest_framework import generics
from mezzanine.generic.models import ThreadedComment
from .serializers import ThreadedCommentSerializer


class ThreadedCommentAPIView(generics.ListAPIView):
    queryset = ThreadedComment.objects.all()
    serializer_class = ThreadedCommentSerializer
