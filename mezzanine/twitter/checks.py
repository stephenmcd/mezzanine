from django.core.checks import Warning, register

from mezzanine.conf import settings

TWITTER_DEPRECATED = Warning(
    "'mezzanine.twitter' is deprecated and will be removed in a future version",
    id="mezzanine.twitter.W001",
)


@register()
def check_twitter(app_configs, **kwargs):
    issues = []

    if "mezzanine.twitter" in settings.INSTALLED_APPS:
        issues.append(TWITTER_DEPRECATED)

    return issues
