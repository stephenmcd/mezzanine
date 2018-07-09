from __future__ import unicode_literals

import pprint

from django import VERSION as DJANGO_VERSION
from django.conf import global_settings
from django.core.checks import Warning, register

from mezzanine.conf import settings
from mezzanine.utils.conf import middlewares_or_subclasses_installed
from mezzanine.utils.sites import SITE_PERMISSION_MIDDLEWARE


@register()
def check_template_settings(app_configs, **kwargs):

    issues = []

    if not settings.TEMPLATES:

        suggested_config = _build_suggested_template_config(settings)

        declaration = 'TEMPLATES = '
        config_formatted = pprint.pformat(suggested_config)
        config_formatted = "\n".join(' ' * len(declaration) + line
                                     for line in config_formatted.splitlines())
        config_formatted = declaration + config_formatted[len(declaration):]

        issues.append(Warning(
            "Please update your settings to use the TEMPLATES setting rather "
            "than the deprecated individual TEMPLATE_ settings. The latter "
            "are unsupported and correct behaviour is not guaranteed. Here's "
            "a suggestion based on on your existing configuration:\n\n%s\n"
            % config_formatted,
            id="mezzanine.core.W01"
        ))

        if settings.DEBUG != settings.TEMPLATE_DEBUG:
            issues.append(Warning(
                "TEMPLATE_DEBUG and DEBUG settings have different values, "
                "which may not be what you want. Mezzanine used to fix this "
                "for you, but doesn't any more. Update your settings.py to "
                "use the TEMPLATES setting to have template debugging "
                "controlled by the DEBUG setting.",
                id="mezzanine.core.W02"
            ))

    else:
        loader_tags_built_in = any(
            'mezzanine.template.loader_tags'
            in config.get('OPTIONS', {}).get('builtins', {})
            for config in settings.TEMPLATES
        )
        if not DJANGO_VERSION < (1, 9) and not loader_tags_built_in:
            issues.append(Warning(
                "You haven't included 'mezzanine.template.loader_tags' as a "
                "builtin in any of your template configurations. Mezzanine's "
                "'overextends' tag will not be available in your templates.",
                id="mezzanine.core.W03"
            ))

    return issues


def _build_suggested_template_config(settings):

    suggested_templates_config = {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "builtins": [
                "mezzanine.template.loader_tags",
            ],
        },
    }

    def set_setting(name, value, unconditional=False):
        if value or unconditional:
            suggested_templates_config[name] = value

    def set_option(name, value):
        if value:
            suggested_templates_config["OPTIONS"][name.lower()] = value

    def get_debug(_):
        if settings.TEMPLATE_DEBUG != settings.DEBUG:
            return settings.TEMPLATE_DEBUG

    def get_default(default):
        def getter(name):
            value = getattr(settings, name)
            if value == getattr(global_settings, name):
                value = default
            return value
        return getter

    default_context_processors = [
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.static",
        "django.core.context_processors.media",
        "django.core.context_processors.request",
        "django.core.context_processors.tz",
        "mezzanine.conf.context_processors.settings",
        "mezzanine.pages.context_processors.page",
    ]

    def get_loaders(_):
        """
        Django's default TEMPLATES setting doesn't specify loaders, instead
        dynamically sets a default based on whether or not APP_DIRS is True.
        We check here if the existing TEMPLATE_LOADERS setting matches one
        of those default cases, and omit the 'loaders' option if so.
        """
        template_loaders = list(settings.TEMPLATE_LOADERS)
        default_loaders = list(global_settings.TEMPLATE_LOADERS)

        if template_loaders == default_loaders:
            # Equivalent to Django's default with APP_DIRS True
            template_loaders = None
            app_dirs = True
        elif template_loaders == default_loaders[:1]:
            # Equivalent to Django's default with APP_DIRS False
            template_loaders = None
            app_dirs = False
        else:
            # This project has a custom loaders setting, which we'll use.
            # Custom loaders are incompatible with APP_DIRS.
            app_dirs = False

        return template_loaders, app_dirs

    def set_loaders(name, value):
        template_loaders, app_dirs = value
        set_option(name, template_loaders)
        set_setting('APP_DIRS', app_dirs, unconditional=True)

    old_settings = [
        ('ALLOWED_INCLUDE_ROOTS', settings.__getattr__, set_option),
        ('TEMPLATE_STRING_IF_INVALID', settings.__getattr__, set_option),
        ('TEMPLATE_DIRS', settings.__getattr__, set_setting),
        ('TEMPLATE_CONTEXT_PROCESSORS',
            get_default(default_context_processors), set_option),
        ('TEMPLATE_DEBUG', get_debug, set_option),
        ('TEMPLATE_LOADERS', get_loaders, set_loaders),
    ]

    def convert_setting_name(old_name):
        return old_name.rpartition('TEMPLATE_')[2]

    for setting_name, getter, setter in old_settings:
        value = getter(setting_name)
        new_setting_name = convert_setting_name(setting_name)
        setter(new_setting_name, value)

    return [suggested_templates_config]


@register()
def check_sites_middleware(app_configs, **kwargs):

    if not middlewares_or_subclasses_installed([SITE_PERMISSION_MIDDLEWARE]):
        return [Warning(SITE_PERMISSION_MIDDLEWARE +
                        " missing from settings.MIDDLEWARE - per site"
                        " permissions not applied",
                        id="mezzanine.core.W04")]
    return []
