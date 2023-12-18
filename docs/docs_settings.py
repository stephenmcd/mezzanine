# flake8: noqa

"""
This is the local_settings file for Mezzanine's docs.
"""

from random import choice

from mezzanine.project_template.project_name.settings import *

DEBUG = False
ROOT_URLCONF = "mezzanine.project_template.project_name.urls"

characters = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
# Generate a SECRET_KEY for this build
SECRET_KEY = "".join(choice(characters) for i in range(50))

if "mezzanine.accounts" not in INSTALLED_APPS:
    INSTALLED_APPS = tuple(INSTALLED_APPS) + ("mezzanine.accounts",)

if "mezzanine.twitter" not in INSTALLED_APPS:
    INSTALLED_APPS = tuple(INSTALLED_APPS) + ("mezzanine.twitter",)
