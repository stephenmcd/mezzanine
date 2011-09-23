
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_app
from django.core.management import call_command
from django.db.models.signals import post_syncdb

from mezzanine.pages.models import Page
from mezzanine.pages import models as pages_app


def create_user(app, created_models, verbosity, interactive, **kwargs):
    if settings.DEBUG and User in created_models and not interactive:
        if User.objects.count() > 0:
            return
        if verbosity >= 1:
            print
            print ("Creating default account "
                   "(username: admin / password: default) ...")
            print
        args = "admin", "example@example.com", "default"
        User.objects.create_superuser(*args)


def create_pages(app, created_models, verbosity, interactive, **kwargs):
    if settings.DEBUG and Page in created_models:
        if interactive:
            confirm = raw_input("\nWould you like to install some initial "
                                "content?\nEg: About page, Blog, Contact "
                                "form. (yes/no): ")
            while True:
                if confirm == "yes":
                    break
                elif confirm == "no":
                    return
                confirm = raw_input("Please enter either 'yes' or 'no': ")
        if verbosity >= 1:
            print
            print ("Creating initial content "
                   "(About page, Blog, Contact form) ...")
            print
        call_command("loaddata", "mezzanine.json")


post_syncdb.connect(create_user, sender=auth_app)
post_syncdb.connect(create_pages, sender=pages_app)
