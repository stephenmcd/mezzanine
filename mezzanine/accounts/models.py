
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from mezzanine.accounts import get_profile_model, get_profile_user_fieldname


# Signal for ensuring users have a profile instance.
Profile = get_profile_model()
if Profile:
    user_field = get_profile_user_fieldname()

    @receiver(post_save, sender=User)
    def user_saved(sender=None, instance=None, **kwargs):
        Profile.objects.get_or_create(**{str(user_field): instance})
