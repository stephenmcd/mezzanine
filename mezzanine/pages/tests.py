from __future__ import unicode_literals
from future.builtins import str

from django.db import connection
from django.template import Context, Template

from mezzanine.conf import settings
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.core.request import current_request
from mezzanine.pages.models import Page, RichTextPage
from mezzanine.urls import PAGES_SLUG
from mezzanine.utils.tests import TestCase
from mezzanine.utils.models import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class PagesTests(TestCase):

    def test_page_ascendants(self):
        """
        Test the methods for looking up ascendants efficiently
        behave as expected.
        """
        # Create related pages.
        primary, created = RichTextPage.objects.get_or_create(title="Primary")
        secondary, created = primary.children.get_or_create(title="Secondary")
        tertiary, created = secondary.children.get_or_create(title="Tertiary")
        # Force a site ID to avoid the site query when measuring queries.
        setattr(current_request(), "site_id", settings.SITE_ID)

        # Test that get_ascendants() returns the right thing.
        page = Page.objects.get(id=tertiary.id)
        ascendants = page.get_ascendants()
        self.assertEqual(ascendants[0].id, secondary.id)
        self.assertEqual(ascendants[1].id, primary.id)

        # Test ascendants are returned in order for slug, using
        # a single DB query.
        connection.queries = []
        pages_for_slug = Page.objects.with_ascendants_for_slug(tertiary.slug)
        self.assertEqual(len(connection.queries), 1)
        self.assertEqual(pages_for_slug[0].id, tertiary.id)
        self.assertEqual(pages_for_slug[1].id, secondary.id)
        self.assertEqual(pages_for_slug[2].id, primary.id)

        # Test page.get_ascendants uses the cached attribute,
        # without any more queries.
        connection.queries = []
        ascendants = pages_for_slug[0].get_ascendants()
        self.assertEqual(len(connection.queries), 0)
        self.assertEqual(ascendants[0].id, secondary.id)
        self.assertEqual(ascendants[1].id, primary.id)

        # Use a custom slug in the page path, and test that
        # Page.objects.with_ascendants_for_slug fails, but
        # correctly falls back to recursive queries.
        secondary.slug += "custom"
        secondary.save()
        pages_for_slug = Page.objects.with_ascendants_for_slug(tertiary.slug)
        self.assertEqual(len(pages_for_slug[0]._ascendants), 0)
        connection.queries = []
        ascendants = pages_for_slug[0].get_ascendants()
        self.assertEqual(len(connection.queries), 2)  # 2 parent queries
        self.assertEqual(pages_for_slug[0].id, tertiary.id)
        self.assertEqual(ascendants[0].id, secondary.id)
        self.assertEqual(ascendants[1].id, primary.id)

    def test_set_parent(self):
        old_parent, _ = RichTextPage.objects.get_or_create(title="Old parent")
        new_parent, _ = RichTextPage.objects.get_or_create(title="New parent")
        child, _ = RichTextPage.objects.get_or_create(
            title="Child", slug="kid")
        self.assertTrue(child.parent is None)
        self.assertTrue(child.slug == "kid")

        child.set_parent(old_parent)
        child.save()
        self.assertEqual(child.parent_id, old_parent.id)
        self.assertTrue(child.slug == "old-parent/kid")

        child = RichTextPage.objects.get(id=child.id)
        self.assertEqual(child.parent_id, old_parent.id)
        self.assertTrue(child.slug == "old-parent/kid")

        child.set_parent(new_parent)
        child.save()
        self.assertEqual(child.parent_id, new_parent.id)
        self.assertTrue(child.slug == "new-parent/kid")

        child = RichTextPage.objects.get(id=child.id)
        self.assertEqual(child.parent_id, new_parent.id)
        self.assertTrue(child.slug == "new-parent/kid")

        child.set_parent(None)
        child.save()
        self.assertTrue(child.parent is None)
        self.assertTrue(child.slug == "kid")

        child = RichTextPage.objects.get(id=child.id)
        self.assertTrue(child.parent is None)
        self.assertTrue(child.slug == "kid")

        child = RichTextPage(title="child2")
        child.set_parent(new_parent)
        self.assertEqual(child.slug, "new-parent/child2")

        # Assert that cycles are detected.
        p1, _ = RichTextPage.objects.get_or_create(title="p1")
        p2, _ = RichTextPage.objects.get_or_create(title="p2")
        p2.set_parent(p1)
        with self.assertRaises(AttributeError):
            p1.set_parent(p1)
        with self.assertRaises(AttributeError):
            p1.set_parent(p2)
        p2c = RichTextPage.objects.get(title="p2")
        with self.assertRaises(AttributeError):
            p1.set_parent(p2c)

    def test_set_slug(self):
        parent, _ = RichTextPage.objects.get_or_create(
            title="Parent", slug="parent")
        child, _ = RichTextPage.objects.get_or_create(
            title="Child", slug="parent/child", parent_id=parent.id)
        parent.set_slug("new-parent-slug")
        parent.save()
        self.assertTrue(parent.slug == "new-parent-slug")

        parent = RichTextPage.objects.get(id=parent.id)
        self.assertTrue(parent.slug == "new-parent-slug")

        child = RichTextPage.objects.get(id=child.id)
        self.assertTrue(child.slug == "new-parent-slug/child")

    def test_login_required(self):

        public, _ = RichTextPage.objects.get_or_create(
            title="Public", slug="public", login_required=False)
        private, _ = RichTextPage.objects.get_or_create(
            title="Private", slug="private", login_required=True)

        args = {"for_user": AnonymousUser()}
        self.assertTrue(public in RichTextPage.objects.published(**args))
        self.assertTrue(not private in RichTextPage.objects.published(**args))
        args = {"for_user": User.objects.get(username=self._username)}
        self.assertTrue(public in RichTextPage.objects.published(**args))
        self.assertTrue(private in RichTextPage.objects.published(**args))
        self.client.logout()

        response = self.client.get(private.get_absolute_url(), follow=True)
        login = "%s?next=%s" % (settings.LOGIN_URL, private.get_absolute_url())
        self.assertRedirects(response, login)
        response = self.client.get(public.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.client.login(username=self._username, password=self._password)
        response = self.client.get(private.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(public.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_page_menu_queries(self):
        """
        Test that rendering a page menu executes the same number of
        queries regardless of the number of pages or levels of
        children.
        """
        template = ('{% load pages_tags %}'
                    '{% page_menu "pages/menus/tree.html" %}')
        before = self.queries_used_for_template(template)
        self.assertTrue(before > 0)
        self.create_recursive_objects(RichTextPage, "parent", title="Page",
                                      status=CONTENT_STATUS_PUBLISHED)
        after = self.queries_used_for_template(template)
        self.assertEqual(before, after)

    def test_page_menu_flags(self):
        """
        Test that pages only appear in the menu templates they've been
        assigned to show in.
        """
        menus = []
        pages = []
        template = "{% load pages_tags %}"
        for i, label, path in settings.PAGE_MENU_TEMPLATES:
            menus.append(i)
            pages.append(RichTextPage.objects.create(in_menus=list(menus),
                title="Page for %s" % str(label),
                status=CONTENT_STATUS_PUBLISHED))
            template += "{%% page_menu '%s' %%}" % path
        rendered = Template(template).render(Context({}))
        for page in pages:
            self.assertEqual(rendered.count(page.title), len(page.in_menus))

    def test_page_menu_default(self):
        """
        Test that the default value for the ``in_menus`` field is used
        and that it doesn't get forced to unicode.
        """
        old_menu_temp = settings.PAGE_MENU_TEMPLATES
        old_menu_temp_def = settings.PAGE_MENU_TEMPLATES_DEFAULT
        try:
            # MenusField initializes choices and default during model
            # loading, so we can't just override settings.
            from mezzanine.pages.models import BasePage
            from mezzanine.pages.fields import MenusField
            settings.PAGE_MENU_TEMPLATES = ((8, 'a', 'a'), (9, 'b', 'b'))

            settings.PAGE_MENU_TEMPLATES_DEFAULT = None

            class P1(BasePage):
                in_menus = MenusField(blank=True, null=True)
            self.assertEqual(P1().in_menus[0], 8)

            settings.PAGE_MENU_TEMPLATES_DEFAULT = tuple()

            class P2(BasePage):
                in_menus = MenusField(blank=True, null=True)
            self.assertEqual(P2().in_menus, None)

            settings.PAGE_MENU_TEMPLATES_DEFAULT = [9]

            class P3(BasePage):
                in_menus = MenusField(blank=True, null=True)
            self.assertEqual(P3().in_menus[0], 9)
        finally:
            settings.PAGE_MENU_TEMPLATES = old_menu_temp
            settings.PAGE_MENU_TEMPLATES_DEFAULT = old_menu_temp_def

    def test_overridden_page(self):
        """
        Test that a page with a slug matching a non-page urlpattern
        return ``True`` for its overridden property.
        """
        # BLOG_SLUG is empty then urlpatterns for pages are prefixed
        # with PAGE_SLUG, and generally won't be overridden. In this
        # case, there aren't any overridding URLs by default, so bail
        # on the test.
        if PAGES_SLUG:
            return
        page, created = RichTextPage.objects.get_or_create(slug="edit")
        self.assertTrue(page.overridden())

    def test_unicode_slug_parm_to_processor_for(self):
        """
        Test that passing an unicode slug to processor_for works for
        python 2.x
        """
        from mezzanine.pages.page_processors import processor_for

        @processor_for(u'test unicode string')
        def test_page_processor(request, page):
            return {}

        page, _ = RichTextPage.objects.get_or_create(title="test page")
        self.assertEqual(test_page_processor(current_request(), page), {})
