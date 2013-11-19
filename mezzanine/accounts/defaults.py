"""
Default settings for all mezzanine.accounts app. Each of these can be
overridden in your project's settings module, just like regular
Django settings. The ``editable`` argument for each controls whether
the setting is editable via Django's admin.

Thought should be given to how a setting is actually used before
making it editable, as it may be inappropriate - for example settings
that are only read during startup shouldn't be editable, since changing
them would require an application reload.
"""
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


register_setting(
    name="ACCOUNTS_MIN_PASSWORD_LENGTH",
    description=_("Minimum length for passwords"),
    editable=False,
    default=6,
)

register_setting(
    name="ACCOUNTS_NO_USERNAME",
    description=_("If ``True``, the username field will be excluded "
        "from sign up and account update forms."),
    editable=False,
    default=False,
)

register_setting(
    name="ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS",
    description=_("List of fields to exclude from the profile form."),
    editable=False,
    default=(),
)

register_setting(
    name="ACCOUNTS_PROFILE_FORM_CLASS",
    description=_("Dotted package path and class name of profile form to use "
        "for users signing up and updating their profile, when "
        "``mezzanine.accounts`` is installed."),
    editable=False,
    default="mezzanine.accounts.forms.ProfileForm",
)

register_setting(
    name="ACCOUNTS_PROFILE_VIEWS_ENABLED",
    description=_("If ``True``, users will have their own public profile "
        "pages."),
    editable=False,
    default=False,
)

register_setting(
    name="ACCOUNTS_VERIFICATION_REQUIRED",
    description=_("If ``True``, when users create an account, they will be "
        "sent an email with a verification link, which they must click to "
        "enable their account."),
    editable=False,
    default=False,
)

register_setting(
    name="ACCOUNTS_APPROVAL_REQUIRED",
    description=_("If ``True``, when users create an account, they will "
        "not be enabled by default and a staff member will need to activate "
        "their account in the admin interface."),
    editable=False,
    default=False,
)

register_setting(
    name="ACCOUNTS_APPROVAL_EMAILS",
    label=_("Account approval email addresses"),
    description=_("A comma separated list of email addresses that "
                  "will receive an email notification each time a "
                  "new account is created that requires approval."),
    editable=True,
    default="",
)
