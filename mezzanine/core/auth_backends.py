
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.utils.http import base36_to_int


class MezzanineBackend(ModelBackend):
    """
    Extends Django's ``ModelBackend`` to allow login via username,
    email, or verification token.

    Args are either ``username`` and ``password``, or ``uidb36``
    and ``token``. In either case, ``is_active`` can also be given.

    For login, is_active is not given, so that the login form can
    raise a specific error for inactive users.
    For password reset, True is given for is_active.
    For signup verficiation, False is given for is_active.
    """

    def authenticate(self, **kwargs):
        if kwargs:
            username = kwargs.pop("username", None)
            if username:
                username_or_email = Q(username=username) | Q(email=username)
                password = kwargs.pop("password", None)
                try:
                    user = User.objects.get(username_or_email, **kwargs)
                except User.DoesNotExist:
                    pass
                else:
                    if user.check_password(password):
                        return user
            else:
                if 'uidb36' not in kwargs:
                    return
                kwargs["id"] = base36_to_int(kwargs.pop("uidb36"))
                token = kwargs.pop("token")
                try:
                    user = User.objects.get(**kwargs)
                except User.DoesNotExist:
                    pass
                else:
                    if default_token_generator.check_token(user, token):
                        return user
