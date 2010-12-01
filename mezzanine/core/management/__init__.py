
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_app
from django.core.management import call_command
from django.db.models.signals import post_syncdb

from mezzanine.pages.models import Page
from mezzanine.pages import models as pages_app


def create_demo_user(app, created_models, verbosity, **kwargs):
    if settings.DEBUG and User in created_models and not kwargs.get("interactive"):
        print 
        print "Creating default account (username: admin / password: default)"
        print 
        User.objects.create_superuser("admin", "example@example.com", "default")


def create_initial_pages(app, created_models, verbosity, **kwargs):
    if settings.DEBUG and Page in created_models:
        if kwargs.get("interactive"):
            confirm = raw_input("\nWould you like to install some initial "
                                "content?\nEg: About page, Blog, Contact " 
                                "form. (yes/no): ")
            while True:
                if confirm == "yes":
                    break
                elif confirm == "no":
                    return
                confirm = raw_input("Please enter either 'yes' or 'no': ")
        print 
        print "Creating initial content (About page, Blog, Contact form)."
        print 
        call_command("loaddata", "mezzanine.json")


post_syncdb.connect(create_demo_user, sender=auth_app)
post_syncdb.connect(create_initial_pages, sender=pages_app)
