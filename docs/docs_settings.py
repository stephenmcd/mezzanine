"""
This is the local_settings file for Mezzanine's docs.
"""

from mezzanine.project_template.project_name.settings import *

ROOT_URLCONF = "mezzanine.project_template.project_name.urls"

# Generate a SECRET_KEY for this build
from random import choice
characters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
SECRET_KEY = ''.join([choice(characters) for i in range(50)])

if "mezzanine.accounts" not in INSTALLED_APPS:
    INSTALLED_APPS = tuple(INSTALLED_APPS) + ("mezzanine.accounts",)
