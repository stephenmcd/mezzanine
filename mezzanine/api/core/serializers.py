from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = User
        fields = ['username']


class SiteSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Site
