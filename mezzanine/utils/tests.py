import os
from shutil import copyfile, copytree

from django.contrib.auth import get_user_model
from django.db import connection
from django.template import Context, Template
from django.test import TestCase as BaseTestCase
from django.test.client import RequestFactory

from mezzanine.conf import settings
from mezzanine.utils.importing import path_for_import


class TestCase(BaseTestCase):
    """
    This is the base test case providing common features for all tests
    across the different apps in Mezzanine.
    """

    def setUp(self):
        """
        Creates an admin user, sets up the debug cursor, so that we can
        track the number of queries used in various places, and creates
        a request factory for views testing.
        """
        self._username = "test"
        self._password = "test"
        self._emailaddress = "example@example.com"
        args = (self._username, self._emailaddress, self._password)
        self._user = get_user_model().objects.create_superuser(*args)
        self._request_factory = RequestFactory()
        self._debug_cursor = connection.force_debug_cursor
        connection.force_debug_cursor = True

    def tearDown(self):
        """
        Clean up the admin user created and debug cursor.
        """
        self._user.delete()
        connection.force_debug_cursor = self._debug_cursor

    def queries_used_for_template(self, template, **context):
        """
        Return the number of queries used when rendering a template
        string.
        """
        connection.queries_log.clear()
        t = Template(template)
        t.render(Context(context))
        return len(connection.queries)

    def create_recursive_objects(self, model, parent_field, **kwargs):
        """
        Create multiple levels of recursive objects.
        """
        per_level = list(range(3))
        for _ in per_level:
            kwargs[parent_field] = None
            level1 = model.objects.create(**kwargs)
            for _ in per_level:
                kwargs[parent_field] = level1
                level2 = model.objects.create(**kwargs)
                for _ in per_level:
                    kwargs[parent_field] = level2
                    model.objects.create(**kwargs)


def copy_test_to_media(module, name):
    """
    Copies a file from Mezzanine's test data path to MEDIA_ROOT.
    Used in tests and demo fixtures.
    """
    mezzanine_path = path_for_import(module)
    test_path = os.path.join(mezzanine_path, "static", "test", name)
    to_path = os.path.join(settings.MEDIA_ROOT, name)
    to_dir = os.path.dirname(to_path)
    if not os.path.exists(to_dir):
        os.makedirs(to_dir)
    if os.path.isdir(test_path):
        copy = copytree
    else:
        copy = copyfile
    try:
        copy(test_path, to_path)
    except OSError:
        pass
