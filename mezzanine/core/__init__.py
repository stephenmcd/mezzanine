"""
Provides abstract models and admin features used throughout the various
Mezzanine apps.
"""

from mezzanine import __version__

# This run admin.site monkey patching
import auth_backends
auth_backends
