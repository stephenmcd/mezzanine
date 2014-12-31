from rest_framework import serializers

from mezzanine.api.core.serializers import UserSerializer

from mezzanine.generic.models import ThreadedComment


class ThreadedCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user')

    class Meta:
        model = ThreadedComment
        fields = ['id', 'comment', 'user_name', 'user', 'replied_to',
                  'submit_date', 'is_public', 'is_removed']
