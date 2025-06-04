====================
Public User Accounts
====================

Mezzanine provides the ability for public users to create their own
accounts for logging into your Mezzanine powered site. Features that can
be restricted to logged-in users include the ability to post comments,
make purchases (using `Cartridge <http://cartridge.jupo.org>`_), view
restricted pages, and anything else you'd like to implement.  You can also
define what a user's profile consists of, allowing users to create their
own profile page for their account.

The accounts functionality is provided by the app
:mod:`mezzanine.accounts`. Adding it to your
:django:setting:`INSTALLED_APPS` setting will enable signup, login,
account updating, and password retrieval features for the public site.

Profiles
========

Profiles are implemented via the :ref:`ACCOUNTS_PROFILE_MODEL` setting.
With :mod:`mezzanine.accounts` installed, you can create a profile model
in one of your apps, with each of the profile fields defined, as well
as a related field to Django's user model. For example suppose we
wanted to capture bios and dates of birth for each user::

    # In myapp/models.py

    from django.db import models

    class MyProfile(models.Model):
        user = models.OneToOneField("auth.User")
        date_of_birth = models.DateField(null=True)
        bio = models.TextField()


    # In settings.py

    INSTALLED_APPS = (
        "myapp",
        "mezzanine.accounts",
        # Many more
    )

    ACCOUNTS_PROFILE_MODEL = "myapp.MyProfile"

The bio and date of birth fields will be available in the signup and
update profile forms, as well as in the user's public profile page.

.. note::

    By default users will only be able to view and edit their own profile
    information. The setting :ref:`ACCOUNTS_PROFILE_VIEWS_ENABLED` can be set
    to ``True`` to enable public profile pages.

Restricting Account Fields
==========================

By default, Mezzanine will expose all relevant user and profile fields
available in the signup and update profile forms, and the user's
profile page. However you may want to store extra fields in user
profiles, but not expose these fields to the user. You may also want to
have no profile model at all, and strip the signup and update profile
forms down to only the minimum required fields on the user model, such
as username and password.

Mezzanine defines the setting :ref:`ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS`
which allows you to define a sequence of field names, for both the user
and profile models, that won't be exposed to the user in any way.
Suppose we define a ``DateTimeField`` on the profile model called
``signup_date`` which we don't want exposed. We also might not bother
asking the user for their first and last name, which are fields defined by
Django's user model. In our ``settings.py`` module we would define::

    ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS = (
        "first_name",
        "last_name",
        "signup_date",
    )

If you don't want to expose the ``username`` field to the user, Mezzanine
provides the setting :ref:`ACCOUNTS_NO_USERNAME`, which when set to
``True``, will expose the ``email`` field as the sole login for the user.

To further customize the profile form you can provide a custom form class using
the :ref:`ACCOUNTS_PROFILE_FORM_CLASS` setting.

Account Verification
====================

By default, with :mod:`mezzanine.accounts` installed, any public visitor
to the site can sign up for an account and will be logged in after
signup. However you may wish to validate that new accounts are only
created by real people with real email addresses. To enable this,
Mezzanine provides the setting :ref:`ACCOUNTS_VERIFICATION_REQUIRED`,
which when set to ``True``, will send new user an email with a
verification link that they must click on, in order to activate their
account.

Account Approval
================

You may also wish to manually activate newly created public accounts.
To enable this, Mezzanine provides the setting
:ref:`ACCOUNTS_APPROVAL_REQUIRED`, which when set to ``True``, will set
newly created accounts as inactive, requiring a staff member to activate
each account in the admin interface. A list of email addresses can be
configured in the Settings section of the admin, which will then be notified by
email each time a new account is created and requires activation. Users
are then sent a notification when their accounts are activated by a staff
member.

