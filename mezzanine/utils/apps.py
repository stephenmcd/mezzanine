from django.conf import settings


def accounts_installed():
    return "mezzanine.accounts" in settings.INSTALLED_APPS


def pages_installed():
    """Detects any of the vanilla pages app or a complete replacement."""
    # At this point Django is not ready to ask for a Page model
    # This means you'll have to leave "mezzanine.pages" even if you
    # swap all of the models
    return "mezzanine.pages" in settings.INSTALLED_APPS


def blog_installed():
    """Detects any of the vanilla blog app or a complete replacement."""
    # At this point Django is not ready to ask for a Page model
    # This means you'll have to leave "mezzanine.blog" even if you
    # swap all of the models
    return "mezzanine.blog" in settings.INSTALLED_APPS
