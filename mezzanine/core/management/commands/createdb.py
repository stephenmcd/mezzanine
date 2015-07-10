from __future__ import print_function, unicode_literals
from future.builtins import int, input

from optparse import make_option
from socket import gethostname

from django import VERSION
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.commands import migrate
from django.db import connection

from mezzanine.conf import settings
from mezzanine.utils.tests import copy_test_to_media


DEFAULT_USERNAME = "admin"
DEFAULT_EMAIL = "example@example.com"
DEFAULT_PASSWORD = "default"


class Command(BaseCommand):

    help = "Performs initial Mezzanine database setup."
    can_import_settings = True

    def __init__(self, *args, **kwargs):
        """
        Adds extra command options (executed only by Django <= 1.7).
        """
        super(Command, self).__init__(*args, **kwargs)
        if VERSION[0] == 1 and VERSION[1] <= 7:
            self.option_list = migrate.Command.option_list + (
                make_option("--nodata", action="store_true", dest="nodata",
                    default=False, help="Do not add demo data."),)

    def add_arguments(self, parser):
        """
        Adds extra command options (executed only by Django >= 1.8).
        """
        parser.add_argument("--nodata", action="store_true", dest="nodata",
            default=False, help="Do not add demo data.")
        parser.add_argument("--noinput", action="store_false",
            dest="interactive", default=True, help="Do not prompt the user "
            "for input of any kind.")

    def handle(self, **options):

        if "conf_setting" in connection.introspection.table_names():
            raise CommandError("Database already created, you probably "
                               "want the migrate command")

        self.verbosity = int(options.get("verbosity", 0))
        self.interactive = int(options.get("interactive", 0))
        self.no_data = int(options.get("nodata", 0))

        call_command("migrate", verbosity=self.verbosity,
                     interactive=self.interactive)

        mapping = [
            [self.create_site, ["django.contrib.sites"]],
            [self.create_user, ["django.contrib.auth"]],
            [self.translation_fields, ["modeltranslation"]],
            [self.create_pages, ["mezzanine.pages", "mezzanine.forms",
                                 "mezzanine.blog", "mezzanine.galleries"]],
            [self.create_shop, ["cartridge.shop"]],
        ]

        for func, apps in mapping:
            if set(apps).issubset(set(settings.INSTALLED_APPS)):
                func()

    def confirm(self, prompt):
        if not self.interactive:
            return True
        confirm = input(prompt)
        while confirm not in ("yes", "no"):
            confirm = input("Please enter either 'yes' or 'no': ")
        return confirm == "yes"

    def create_site(self):
        domain = "127.0.0.1:8000" if settings.DEBUG else gethostname()
        if self.interactive:
            entered = input("\nA site record is required.\nPlease "
                              "enter the domain and optional port in "
                              "the format 'domain:port'.\nFor example "
                              "'localhost:8000' or 'www.example.com'. "
                              "\nHit enter to use the default (%s): " %
                            domain)
            if entered:
                domain = entered.strip("': ")
        if self.verbosity >= 1:
            print("\nCreating default site record: %s ...\n" % domain)
        try:
            site = Site.objects.get()
        except Site.DoesNotExist:
            site = Site()
        site.name = "Default"
        site.domain = domain
        site.save()

    def create_user(self):
        User = get_user_model()
        if not settings.DEBUG or User.objects.count() > 0:
            return
        if self.confirm("Would you like the default admin account created? "
                        "(yes/no): "):
            if self.verbosity >= 1:
                print("\nCreating default account "
                      "(username: %s / password: %s) ...\n" %
                      (DEFAULT_USERNAME, DEFAULT_PASSWORD))
            args = (DEFAULT_USERNAME, DEFAULT_EMAIL, DEFAULT_PASSWORD)
            User.objects.create_superuser(*args)

    def create_pages(self):
        call_command("loaddata", "mezzanine_required.json")
        install_optional = not self.no_data and self.confirm(
            "\nWould you like to install some initial "
            "demo pages?\nEg: About us, Contact form, "
            "Gallery. (yes/no): ")
        if install_optional:
            if self.verbosity >= 1:
                print("\nCreating demo pages: About us, Contact form, "
                        "Gallery ...\n")
            from mezzanine.galleries.models import Gallery
            call_command("loaddata", "mezzanine_optional.json")
            zip_name = "gallery.zip"
            copy_test_to_media("mezzanine.core", zip_name)
            gallery = Gallery.objects.get()
            gallery.zip_import = zip_name
            gallery.save()

    def create_shop(self):
        call_command("loaddata", "cartridge_required.json")
        install_optional = not self.no_data and self.confirm(
            "\nWould you like to install an initial "
            "demo product and sale? (yes/no): ")
        if install_optional:
            if self.verbosity >= 1:
                print("\nCreating demo product and sale ...\n")
            call_command("loaddata", "cartridge_optional.json")
            copy_test_to_media("cartridge.shop", "product")

    def translation_fields(self):
        try:
            from modeltranslation.management.commands \
                    import (update_translation_fields as update_fields,
                            sync_translation_fields as create_fields)
        except ImportError:
            return
        update = self.confirm(
            "\nDjango-modeltranslation is installed for "
            "this project and you have specified to use "
            "i18n.\nWould you like to update translation "
            "fields from the default ones? (yes/no): ")
        if update:
            create_fields.Command().execute(
                    verbosity=self.verbosity, interactive=False)
            update_fields.Command().execute(verbosity=self.verbosity)
