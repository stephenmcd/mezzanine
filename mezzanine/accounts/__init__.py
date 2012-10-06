"""
Provides features for non-staff user accounts, such as login, signup
with optional email verification, password reset, and integration
with user profiles models defined by the ``AUTH_PROFILE_MODULE``
setting. Some utility functions for probing the profile model are
included below.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

from mezzanine.utils.importing import import_dotted_path


def get_profile_model():
    """
    Returns the profile model defined by the ``AUTH_PROFILE_MODULE``
    setting, or ``None`` if no profile model is defined.
    """
    profile_model = getattr(settings, "AUTH_PROFILE_MODULE", None)
    if profile_model:
        if profile_model and profile_model.count(".") == 1:
            Profile = get_model(*profile_model.split("."))
            if Profile is not None:
                return Profile
        raise ImproperlyConfigured("Value for AUTH_PROFILE_MODULE could "
                                   "not be loaded: %s" % profile_model)


def get_profile_form():
    """
    Returns the profile form defined by ``ACCOUNTS_PROFILE_FORM_CLASS``.
    """
    from mezzanine.conf import settings
    try:
        return import_dotted_path(settings.ACCOUNTS_PROFILE_FORM_CLASS)
    except ImportError:
        raise ImproperlyConfigured("Value for ACCOUNTS_PROFILE_FORM_CLASS "
                                   "could not be imported: %s" %
                                   settings.ACCOUNTS_PROFILE_FORM_CLASS)


def get_profile_user_fieldname():
    """
    Returns the name of the first field on the profile model that
    points to the ``auth.User`` model.
    """
    Profile = get_profile_model()
    if Profile is not None:
        for field in Profile._meta.fields:
            if field.rel and field.rel.to == User:
                return field.name
    raise ImproperlyConfigured("Value for AUTH_PROFILE_MODULE does not "
                               "contain a ForeignKey field for auth.User: %s"
                               % Profile.__name__)
