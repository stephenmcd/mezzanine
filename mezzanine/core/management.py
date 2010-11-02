
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_app
from django.db.models.signals import post_syncdb


def create_demo_user(app, created_models, verbosity, **kwargs):
    if settings.DEBUG and User in created_models and not kwargs.get("interactive"):
        print 
        print "Creating default account (username: admin / password: default)"
        print 
        User.objects.create_superuser("admin", "example@example.com", "default")


post_syncdb.connect(create_demo_user, sender=auth_app)
