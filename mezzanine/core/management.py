
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_app
from django.db.models.signals import post_syncdb


def create_demo_user(app, created_models, verbosity, db, **kwargs):
    if settings.DEBUG and User in created_models:
        if verbosity >= 2:
            print "Creating demo User object"
        User.objects.create_superuser("demo", "example@example.com", "demo")


post_syncdb.connect(create_demo_user, sender=auth_app)
