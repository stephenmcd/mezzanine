from __future__ import unicode_literals
from future.builtins import str

from django.db import connection
from django.db.models.signals import post_save
from django.db.utils import DatabaseError
from django.dispatch import receiver

from mezzanine.conf import settings
from mezzanine.utils.models import lazy_model_ops
from mezzanine.accounts import get_profile_user_fieldname


if getattr(settings, "AUTH_PROFILE_MODULE", None):

    def wait_for_user_model(user_model):

        def wait_for_profile_model(profile_model):

            user_field = get_profile_user_fieldname(profile_model, user_model)

            def create_profile_instance(_, user_instance=None, **kwargs):
                try:
                    kwargs = {str(user_field): user_instance}
                    profile_model.objects.get_or_create(**kwargs)
                except DatabaseError:
                    # User creation in initial syncdb may have been triggered,
                    # while profile model is under migration management and
                    # doesn't exist yet. We close the connection so that it
                    # gets re-opened, allowing syncdb to continue and complete.
                    connection.close()
            post_save.connect(create_profile_instance)

        lazy_model_ops.add(wait_for_profile_model, settings.AUTH_PROFILE_MODULE)
    lazy_model_ops.add(wait_for_user_model, settings.AUTH_USER_MODEL)
