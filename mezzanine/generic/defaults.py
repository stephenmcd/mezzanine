"""
Default settings for the ``mezzanine.generic`` app. Each of these can be
overridden in your project's settings module, just like regular
Django settings. The ``editable`` argument for each controls whether
the setting is editable via Django's admin.

Thought should be given to how a setting is actually used before
making it editable, as it may be inappropriate - for example settings
that are only read during startup shouldn't be editable, since changing
them would require an application reload.
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


generic_comments = getattr(settings, "COMMENTS_APP", "") == "mezzanine.generic"

if generic_comments:
    register_setting(
        name="COMMENTS_ACCOUNT_REQUIRED",
        label=_("Accounts required for commenting"),
        description=_("If ``True``, users must log in to comment."),
        editable=True,
        default=False,
    )

    register_setting(
        name="COMMENTS_DISQUS_SHORTNAME",
        label=_("Disqus shortname"),
        description=_("Shortname for the http://disqus.com comments "
                      "service."),
        editable=True,
        default="",
    )

    register_setting(
        name="COMMENTS_DISQUS_API_PUBLIC_KEY",
        label=_("Disqus public key"),
        description=_("Public key for http://disqus.com developer API"),
        editable=True,
        default="",
    )

    register_setting(
        name="COMMENTS_DISQUS_API_SECRET_KEY",
        label=_("Disqus secret key"),
        description=_("Secret key for http://disqus.com developer API"),
        editable=True,
        default="",
    )

    register_setting(
        name="COMMENTS_DEFAULT_APPROVED",
        label=_("Auto-approve comments"),
        description=_("If ``True``, built-in comments are approved by "
                      "default."),
        editable=True,
        default=True,
    )

    register_setting(
        name="COMMENT_FILTER",
        description=_("Dotted path to the function to call on a comment's "
            "value before it is rendered to the template."),
        editable=False,
        default=None,
    )

    register_setting(
        name="COMMENTS_NOTIFICATION_EMAILS",
        label=_("Comment notification email addresses"),
        description=_("A comma separated list of email addresses that "
                      "will receive an email notification each time a "
                      "new comment is posted on the site."),
        editable=True,
        default="",
    )

    register_setting(
        name="COMMENTS_NUM_LATEST",
        label=_("Admin comments"),
        description=_("Number of latest comments shown in the admin "
                      "dashboard."),
        editable=True,
        default=5,
    )

    register_setting(
        name="COMMENTS_UNAPPROVED_VISIBLE",
        label=_("Show unapproved comments"),
        description=_("If ``True``, comments that have ``is_public`` "
            "unchecked will still be displayed, but replaced with a "
            "``waiting to be approved`` message."),
        editable=True,
        default=True,
    )

    register_setting(
        name="COMMENTS_REMOVED_VISIBLE",
        label=_("Show removed comments"),
        description=_("If ``True``, comments that have ``removed`` "
                      "checked will still be displayed, but replaced "
                      "with a ``removed`` message."),
        editable=True,
        default=True,
    )

register_setting(
    name="RATINGS_MIN",
    description=_("Min value for a rating."),
    editable=False,
    default=1,
)

register_setting(
    name="RATINGS_MAX",
    description=_("Max value for a rating."),
    editable=False,
    default=5,
)
