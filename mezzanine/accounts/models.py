from __future__ import unicode_literals
from future.builtins import str

from django.db import connection
from django.db.models.signals import post_save
from django.db.utils import DatabaseError
from django.dispatch import receiver

from mezzanine.utils.models import get_user_model
from mezzanine.accounts import get_profile_model, get_profile_user_fieldname


# Signal for ensuring users have a profile instance.
Profile = get_profile_model()
User = get_user_model()

if Profile:
    user_field = get_profile_user_fieldname()

    @receiver(post_save, sender=User)
    def user_saved(sender=None, instance=None, **kwargs):
        try:
            Profile.objects.get_or_create(**{str(user_field): instance})
        except DatabaseError:
            # User creation in initial syncdb may have been triggered,
            # while profile model is under migration management and
            # doesn't exist yet. We close the connection so that it
            # gets re-opened, allowing syncdb to continue and complete.
            connection.close()
