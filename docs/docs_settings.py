"""
This is the local_settings file for Mezzanine's docs.
"""

from mezzanine.project_template.settings import *

# Generate a SECRET_KEY for this build
from random import choice
characters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
SECRET_KEY = ''.join([choice(characters) for i in range(50)])
