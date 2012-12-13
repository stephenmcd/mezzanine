
from socket import gethostname

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_app
from django.contrib.sites.models import Site
from django.contrib.sites.management import create_default_site
from django.contrib.sites import models as sites_app
from django.core.management import call_command
from django.db.models.signals import post_syncdb

from mezzanine.pages.models import Page

from mezzanine.pages import models as pages_app
from mezzanine.utils.tests import copy_test_to_media


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
    from mezzanine.forms.models import Form
    from mezzanine.galleries.models import Gallery

    required = set([Page, Form, Gallery])
    if required.issubset(set(created_models)):
        call_command("loaddata", "mezzanine_required.json")
        if interactive:
            confirm = raw_input("\nWould you like to install some initial "
                                "content?\nEg: About page, Blog, Contact "
                                "form, Gallery. (yes/no): ")
            while True:
                if confirm == "yes":
                    break
                elif confirm == "no":
                    return
                confirm = raw_input("Please enter either 'yes' or 'no': ")
            install_optional_data(verbosity)


def create_site(app, created_models, verbosity, interactive, **kwargs):
    if Site in created_models:
        domain = "127.0.0.1:8000" if settings.DEBUG else gethostname()
        if interactive:
            entered = raw_input("\nA site record is required. Please enter "
                                "the domain and optional port in the format "
                                "'domain:port'. For example 'localhost:8000' "
                                "or 'www.example.com'. Hit enter to use the "
                                "default (%s): " % domain)
            if entered:
                domain = entered.strip("': ")
        if verbosity >= 1:
            print
            print "Creating default Site %s ... " % domain
            print
        Site.objects.create(name="Default", domain=domain)


def install_optional_data(verbosity):
    from mezzanine.galleries.models import Gallery

    call_command("loaddata", "mezzanine_optional.json")
    zip_name = "gallery.zip"
    copy_test_to_media("mezzanine.core", zip_name)
    gallery = Gallery.objects.get()
    gallery.zip_import = zip_name
    gallery.save()
    if verbosity >= 1:
        print
        print ("Creating demo content "
               "(About page, Blog, Contact form, Gallery) ...")
        print

if not settings.TESTING:
    post_syncdb.connect(create_user, sender=auth_app)
    post_syncdb.connect(create_pages, sender=pages_app)
    post_syncdb.connect(create_site, sender=sites_app)
    post_syncdb.disconnect(create_default_site, sender=sites_app)
