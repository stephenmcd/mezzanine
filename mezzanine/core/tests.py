
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import connection
from django.template import Context, Template, TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.conf import settings, registry
from mezzanine.conf.models import Setting
from mezzanine.core.models import CONTENT_STATUS_DRAFT
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.forms import fields
from mezzanine.forms.models import Form
from mezzanine.pages.models import ContentPage
from mezzanine.utils.tests import run_pyflakes_for_package
from mezzanine.utils.importing import import_dotted_path


class Tests(TestCase):
    """
    Mezzanine tests.
    """

    fixtures = ["mezzanine.json"] # From mezzanine.pages

    def setUp(self):
        """
        Create an admin user.
        """
        self._username = "test"
        self._password = "test"
        args = (self._username, "example@example.com", self._password)
        self._user = User.objects.create_superuser(*args)

    def test_draft_page(self):
        """
        Test a draft page as only being viewable by a staff member.
        """
        self.client.logout()
        draft = ContentPage.objects.create(title="Draft",
                                           status=CONTENT_STATUS_DRAFT)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        self.client.login(username=self._username, password=self._password)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_overridden_page(self):
        """
        Test that a page with a slug matching a non-page urlpattern return
        ``True`` for its overridden property. The blog page from the fixtures
        should satisfy this case.
        """
        blog_page, created = ContentPage.objects.get_or_create(
                                                slug=settings.BLOG_SLUG)
        self.assertTrue(blog_page.overridden())

    def test_description(self):
        """
        Test generated description is first line of content.
        """
        description = "<p>How now brown cow</p>"
        page = ContentPage.objects.create(title="Draft",
                                          content=description * 3)
        self.assertEqual(page.description, description)

    def test_device_specific_template(self):
        """
        Test that an alternate template is rendered when a mobile device is
        used.
        """
        try:
            get_template("mobile/index.html")
        except TemplateDoesNotExist:
            return
        template_name = lambda t: t.name if hasattr(t, "name") else t[0].name
        ua = settings.DEVICE_USER_AGENTS[0][1][0]
        default = self.client.get(reverse("home")).template
        mobile = self.client.get(reverse("home"), HTTP_USER_AGENT=ua).template
        self.assertNotEqual(template_name(default), template_name(mobile))

    def test_blog_views(self):
        """
        Basic status code test for blog views.
        """
        response = self.client.get(reverse("blog_post_list"))
        self.assertEqual(response.status_code, 200)
        blog_post = BlogPost.objects.create(title="Post", user=self._user,
                                            status=CONTENT_STATUS_PUBLISHED)
        response = self.client.get(blog_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def queries_used_for_template(self, template, **context):
        """
        Return the number of queries used when rendering a template string.
        """
        settings.DEBUG = True
        connection.queries = []
        t = Template(template)
        t.render(Context(context))
        settings.DEBUG = False
        return len(connection.queries)

    def create_recursive_objects(self, model, parent_field, **kwargs):
        """
        Create multiple levels of recursive objects.
        """
        per_level = range(3)
        for _ in per_level:
            kwargs[parent_field] = None
            level1 = model.objects.create(**kwargs)
            for _ in per_level:
                kwargs[parent_field] = level1
                level2 = model.objects.create(**kwargs)
                for _ in per_level:
                    kwargs[parent_field] = level2
                    model.objects.create(**kwargs)

    def test_comments(self):
        """
        Test that rendering the blog comments executes the same number of
        queries regardless of the number of nested replies.
        """
        blog_post = BlogPost.objects.create(title="Post", user=self._user)
        template = "{% load blog_tags %}{% blog_comments_for blog_post %}"
        before = self.queries_used_for_template(template, blog_post=blog_post)
        self.create_recursive_objects(Comment, "replied_to", name="Comment",
                                      blog_post=blog_post)
        after = self.queries_used_for_template(template, blog_post=blog_post)
        self.assertEquals(before, after)

    def test_page_menu(self):
        """
        Test that rendering a page menu executes the same number of queries
        regardless of the number of pages or levels of children.
        """
        template = '{% load pages_tags %}{% page_menu "pages/menus/tree.html" %}'
        before = self.queries_used_for_template(template)
        self.create_recursive_objects(ContentPage, "parent", title="Page",
                                      status=CONTENT_STATUS_PUBLISHED)
        after = self.queries_used_for_template(template)
        self.assertEquals(before, after)

    def test_search(self):
        """
        Test search.
        """
        ContentPage.objects.all().delete()
        first = ContentPage.objects.create(title="test page").id
        second = ContentPage.objects.create(title="test another test page").id
        # Either word.
        results = ContentPage.objects.search("another test")
        self.assertEqual(len(results), 2)
        # Must include first word.
        results = ContentPage.objects.search("+another test")
        self.assertEqual(len(results), 1)
        # Mustn't include first word.
        results = ContentPage.objects.search("-another test")
        self.assertEqual(len(results), 1)
        if results:
            self.assertEqual(results[0].id, first)
        # Exact phrase.
        results = ContentPage.objects.search('"another test"')
        self.assertEqual(len(results), 1)
        if results:
            self.assertEqual(results[0].id, second)
        # Test ordering.
        results = ContentPage.objects.search("test")
        self.assertEqual(len(results), 2)
        if results:
            self.assertEqual(results[0].id, second)

    def test_forms(self):
        """
        Simple 200 status check against rendering and posting to forms with
        both optional and required fields.
        """
        for required in (True, False):
            form = Form.objects.create(title="Form",
                                       status=CONTENT_STATUS_PUBLISHED)
            for (i, (field, _)) in enumerate(fields.NAMES):
                form.fields.create(label="Field %s" % i, field_type=field,
                                   required=required, visible=True)
            response = self.client.get(form.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            visible_fields = form.fields.visible()
            data = dict([("field_%s" % f.id, "test") for f in visible_fields])
            response = self.client.post(form.get_absolute_url(), data=data)
            self.assertEqual(response.status_code, 200)

    def test_settings(self):
        """
        Test that an editable setting can be overridden with a DB value and
        that the data type is preserved when the value is returned back out
        of the DB. Also checks to ensure no unsupported types are defined
        for editable settings.
        """
        # Find an editable setting for each supported type.
        names_by_type = {}
        for setting in registry.values():
            if setting["editable"] and setting["type"] not in names_by_type:
                names_by_type[setting["type"]] = setting["name"]
        # Create a modified value for each setting and save it.
        values_by_name = {}
        for (setting_type, setting_name) in names_by_type.items():
            setting_value = registry[setting_name]["default"]
            if setting_type in (int, float):
                setting_value += 1
            elif setting_type is bool:
                setting_value = not setting_value
            elif setting_type in (str, unicode):
                setting_value += "test"
            else:
                self.fail("Unsupported setting type for %s: %s" %
                                                (setting_name, setting_type))
            values_by_name[setting_name] = setting_value
            Setting.objects.create(name=setting_name, value=str(setting_value))
        # Load the settings and make sure the DB values have persisted.
        settings.use_editable()
        for (name, value) in values_by_name.items():
            self.assertEqual(getattr(settings, name), value)

    def test_with_pyflakes(self):
        """
        Run pyflakes across the code base to check for potential errors.
        """
        warnings = run_pyflakes_for_package("mezzanine")
        if warnings:
            warnings.insert(0, "pyflakes warnings:")
            self.fail("\n".join(warnings))

    def test_utils(self):
        """
        Miscellanous tests for the ``mezzanine.utils`` package.
        """
        self.assertRaises(ImportError, import_dotted_path, "mezzanine")
        self.assertRaises(ImportError, import_dotted_path, "mezzanine.NO")
        self.assertRaises(ImportError, import_dotted_path, "mezzanine.core.NO")
        try:
            import_dotted_path("mezzanine.core")
        except ImportError:
                self.fail("mezzanine.utils.imports.import_dotted_path"
                          "could not import \"mezzanine.core\"")
