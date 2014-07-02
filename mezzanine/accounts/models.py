from django.db import DatabaseError, connection
from django.db.models.signals import post_save
from mezzanine.accounts import get_profile_for_user
from mezzanine.conf import settings
from mezzanine.utils.models import lazy_model_ops


__all__ = ()


if getattr(settings, "AUTH_PROFILE_MODULE", None):

    # This will be called when class_prepared signal has been sent
    # for both the profile and user model.
    def wait_for_models(profile_model, user_model):

        def create_profile(sender, instance, created, **_):
            if created:
                try:
                    get_profile_for_user(instance)
                except DatabaseError:
                    # User creation in initial syncdb may have been triggered,
                    # while profile model is under migration management and
                    # doesn't exist yet. We close the connection so that it
                    # gets re-opened, allowing syncdb to continue and complete.
                    connection.close()

        post_save.connect(create_profile, sender=user_model, weak=False)

    lazy_model_ops.add(wait_for_models,
                       settings.AUTH_PROFILE_MODULE, settings.AUTH_USER_MODEL)
