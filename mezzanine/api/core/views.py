from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer


class UserAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
