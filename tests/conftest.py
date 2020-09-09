import os
import shutil
import sys

import django
import pytest

from pathlib import Path

# Path to the temp mezzanine project folder (will be a sibling of this file)
PROJECT_PATH = Path(__file__).parent / "project_name"

TEST_SETTINGS = """
from . import settings

globals().update(i for i in settings.__dict__.items() if i[0].isupper())

# Add our own tests folder to installed apps (required to test models)
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append("tests")

if "mezzanine.accounts" not in INSTALLED_APPS:
    INSTALLED_APPS.append("mezzanine.accounts")

# Use the MD5 password hasher by default for quicker test runs.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)
"""


def pytest_report_header(config):
    """
    Have pytest report the path to the project folder
    """
    return f"mezzanine proj (tmp): {PROJECT_PATH}"


def pytest_configure():
    """
    Hack the `project_template` dir into an actual project to test against.
    """
    from mezzanine.utils.importing import path_for_import

    template_path = (
        Path(path_for_import("mezzanine")) / "project_template" / "project_name"
    )
    shutil.copytree(str(template_path), str(PROJECT_PATH))
    local_settings = (PROJECT_PATH / "local_settings.py.template").read_text()
    (PROJECT_PATH / "test_settings.py").write_text(TEST_SETTINGS + local_settings)

    # Setup the environment for Django
    sys.path.insert(0, str(PROJECT_PATH.parent))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_name.test_settings")
    django.setup()


def pytest_unconfigure():
    """
    Remove the folder folder we copied in `pytest_configure`.
    """
    try:
        shutil.rmtree(str(PROJECT_PATH))
    except OSError:
        pass
