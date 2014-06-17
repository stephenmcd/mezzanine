"""
Provides features for non-staff user accounts, such as login, signup
with optional email verification, password reset, and integration
with user profiles models defined by the ``AUTH_PROFILE_MODULE``
setting. Some utility functions for probing the profile model are
included below.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from mezzanine.utils.models import get_user_model, get_model
from mezzanine.utils.importing import import_dotted_path


def get_profile_model():
    """
    Returns the profile model defined by the ``AUTH_PROFILE_MODULE``
    setting, or ``None`` if no profile model is defined.
    """
    profile_model_name = getattr(settings, "AUTH_PROFILE_MODULE", None)

    if not profile_model_name:
        return None

    try:
        app_label, model_name = profile_model_name.split(".")
        try:
            profile_model = get_model(app_label, model_name)
        except LookupError:
            raise ImproperlyConfigured("No model corresponding to the value "
                                       "of AUTH_PROFILE_MODULE was found.")
        else:
            return profile_model
    except (ValueError, AttributeError):
        raise ImproperlyConfigured("Value for AUTH_PROFILE_MODULE must "
                                   "be an \"app_label.ModelName\" string.")


def get_profile_for_user(user):
    """
    Returns site-specific profile for this user. Raises
    SiteProfileNotAvailable if this site does not allow profiles.
    """
    if not hasattr(user, '_mezzanine_profile'):
        from django.conf import settings
        if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
            raise ImproperlyConfigured(
                'You need to set AUTH_PROFILE_MODULE in your project '
                'settings')

        profile_model = get_profile_model()
        if not profile_model:
            return None

        try:
            user._mezzanine_profile = profile_model._default_manager.using(
                user._state.db).get(user__id__exact=user.id)
            user._mezzanine_profile.user = user
        except (ImportError, ImproperlyConfigured):
            raise ImproperlyConfigured
    return user._mezzanine_profile


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


def get_profile_user_fieldname(profile_model=None, user_model=None):
    """
    Returns the name of the first field on the profile model that
    points to the ``auth.User`` model.
    """
    Profile = profile_model or get_profile_model()
    User = user_model or get_user_model()
    if Profile is not None:
        for field in Profile._meta.fields:
            if field.rel and field.rel.to == User:
                return field.name
    raise ImproperlyConfigured("Value for AUTH_PROFILE_MODULE does not "
                               "contain a ForeignKey field for auth.User: %s"
                               % Profile.__name__)
