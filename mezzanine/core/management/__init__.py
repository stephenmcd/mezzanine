from django.conf import settings
from django.contrib.sites import models as sites_app
from django.contrib.sites.management import create_default_site

try:
    from django.db.models.signals import post_migrate
except ImportError:
    from django.db.models.signals import post_syncdb as post_migrate


if not settings.TESTING:
    post_migrate.disconnect(create_default_site, sender=sites_app)
