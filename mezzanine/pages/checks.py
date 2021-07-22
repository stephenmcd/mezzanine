from django.core.checks import Warning, register

from mezzanine.conf import settings


@register
def check_context_processor(app_configs, **kwargs):

    issues = []

    name = "mezzanine.pages.context_processors.page"

    loaded = any(
        name in config.get("OPTIONS", {}).get("context_processors", {})
        for config in settings.TEMPLATES
    )

    if not loaded:
        issues.append(
            Warning(
                "You haven't included 'mezzanine.pages.context_processors.page' "
                "as a context processor in any of your template configurations. "
                "Your templates might not work as expected.",
                id="mezzanine.pages.W01",
            )
        )

    return issues
