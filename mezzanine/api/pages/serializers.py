from rest_framework import serializers
from mezzanine.pages.models import Page, RichTextPage


class RichTextPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RichTextPage
        fields = ['content']


class PageSerializer(serializers.ModelSerializer):
    richtextpage = RichTextPageSerializer()

    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'parent', 'in_menus',
                  'login_required', 'richtextpage', 'publish_date',
                  'keywords_string']
