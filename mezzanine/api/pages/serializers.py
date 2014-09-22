from rest_framework import serializers
from mezzanine.pages.models import Page
from mezzanine.generic.models import  ThreadedComment

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ThreadedComment