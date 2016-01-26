from __future__ import unicode_literals

from django.core.checks import Warning

from mezzanine.conf import settings


def check_context_processor(app_configs, **kwargs):

    issues = []

    pages_context_processor = 'mezzanine.pages.context_processors.page'

    if settings.TEMPLATES:
        pages_context_processor_loaded = any(
            pages_context_processor in config.get('OPTIONS', {}).get('context_processors', {})
            for config in settings.TEMPLATES
        )
    else:
        pages_context_processor_loaded = pages_context_processor in settings.TEMPLATE_CONTEXT_PROCESSORS

    if not pages_context_processor_loaded:
        issues.append(Warning(
            "You haven't included 'mezzanine.pages.context_processors.page' "
            "as a context processor in any of your template configurations. "
            "Your templates might not work as expected.",
            id="mezzanine.pages.W01"
        ))

    return issues
