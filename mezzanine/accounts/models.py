from django.db import DatabaseError, connection
from django.db.models.signals import post_save
from mezzanine.accounts import get_profile_for_user
from mezzanine.conf import settings


__all__ = ()


if getattr(settings, "ACCOUNTS_PROFILE_MODEL", None):

    def create_profile(**kwargs):
        if kwargs["created"]:
            try:
                get_profile_for_user(kwargs["instance"])
            except DatabaseError:
                # User creation in initial syncdb may have been triggered,
                # while profile model is under migration management and
                # doesn't exist yet. We close the connection so that it
                # gets re-opened, allowing syncdb to continue and complete.
                connection.close()

    post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL,
                      weak=False)
