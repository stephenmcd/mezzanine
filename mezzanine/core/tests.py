
import os
from shutil import rmtree
from urlparse import urlparse
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.urlresolvers import reverse
from django.db import connection
from django.template import Context, Template, TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase
from django.utils.html import strip_tags
from django.utils.http import int_to_base36
from django.contrib.sites.models import Site
from PIL import Image

from mezzanine.accounts import get_profile_model, get_profile_user_fieldname
from mezzanine.blog.models import BlogPost
from mezzanine.conf import settings, registry
from mezzanine.conf.models import Setting
from mezzanine.core.models import CONTENT_STATUS_DRAFT
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
from mezzanine.core.request import current_request
from mezzanine.core.templatetags.mezzanine_tags import thumbnail
from mezzanine.forms import fields
from mezzanine.forms.models import Form
from mezzanine.galleries.models import Gallery, GALLERIES_UPLOAD_DIR
from mezzanine.generic.forms import RatingForm
from mezzanine.generic.models import ThreadedComment, AssignedKeyword, Keyword
from mezzanine.generic.models import RATING_RANGE
from mezzanine.pages.models import Page, RichTextPage
from mezzanine.urls import PAGES_SLUG
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.tests import copy_test_to_media, run_pyflakes_for_package
from mezzanine.utils.tests import run_pep8_for_package


class Tests(TestCase):
    """
    Mezzanine tests.
    """

    def setUp(self):
        """
        Create an admin user.
        """
        connection.use_debug_cursor = True
        self._username = "test"
        self._password = "test"
        args = (self._username, "example@example.com", self._password)
        self._user = User.objects.create_superuser(*args)

    def account_data(self, test_value):
        """
        Returns a dict with test data for all the user/profile fields.
        """
        # User fields
        data = {"email": test_value + "@example.com"}
        for field in ("first_name", "last_name", "username",
                      "password1", "password2"):
            if field.startswith("password"):
                value = "x" * settings.ACCOUNTS_MIN_PASSWORD_LENGTH
            else:
                value = test_value
            data[field] = value
        # Profile fields
        Profile = get_profile_model()
        if Profile is not None:
            user_fieldname = get_profile_user_fieldname()
            for field in Profile._meta.fields:
                if field.name not in (user_fieldname, "id"):
                    if field.choices:
                        value = field.choices[0][0]
                    else:
                        value = test_value
                    data[field.name] = value
        return data

    def test_account(self):
        """
        Test account creation.
        """
        # Verification not required - test an active user is created.

        data = self.account_data("test1")
        settings.ACCOUNTS_VERIFICATION_REQUIRED = False
        response = self.client.post(reverse("signup"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(email=data["email"], is_active=True)
        self.assertEqual(len(users), 1)
        # Verification required - test an inactive user is created,
        settings.ACCOUNTS_VERIFICATION_REQUIRED = True
        data = self.account_data("test2")
        emails = len(mail.outbox)
        response = self.client.post(reverse("signup"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(email=data["email"], is_active=False)
        self.assertEqual(len(users), 1)
        # Test the verification email.
        self.assertEqual(len(mail.outbox), emails + 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], data["email"])
        # Test the verification link.
        new_user = users[0]
        verification_url = reverse("signup_verify", kwargs={
            "uidb36": int_to_base36(new_user.id),
            "token": default_token_generator.make_token(new_user),
        })
        response = self.client.get(verification_url, follow=True)
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(email=data["email"], is_active=True)
        self.assertEqual(len(users), 1)

    def test_draft_page(self):
        """
        Test a draft page as only being viewable by a staff member.
        """
        self.client.logout()
        draft = RichTextPage.objects.create(title="Draft",
                                            status=CONTENT_STATUS_DRAFT)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        self.client.login(username=self._username, password=self._password)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 200)

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
        self.assertEquals(len(pages_for_slug[0]._ascendants), 0)
        connection.queries = []
        ascendants = pages_for_slug[0].get_ascendants()
        self.assertEqual(len(connection.queries), 2)  # 2 parent queries
        self.assertEqual(pages_for_slug[0].id, tertiary.id)
        self.assertEqual(ascendants[0].id, secondary.id)
        self.assertEqual(ascendants[1].id, primary.id)

    def test_description(self):
        """
        Test generated description is text version of the first line
        of content.
        """
        description = "<p>How now brown cow</p>"
        page = RichTextPage.objects.create(title="Draft",
                                           content=description * 3)
        self.assertEqual(page.description, strip_tags(description))

    def test_device_specific_template(self):
        """
        Test that an alternate template is rendered when a mobile
        device is used.
        """
        try:
            get_template("mobile/index.html")
        except TemplateDoesNotExist:
            return
        ua = settings.DEVICE_USER_AGENTS[0][1][0]
        kwargs = {"slug": "device-test"}
        url = reverse("page", kwargs=kwargs)
        kwargs["status"] = CONTENT_STATUS_PUBLISHED
        RichTextPage.objects.get_or_create(**kwargs)
        default = self.client.get(url)
        mobile = self.client.get(url, HTTP_USER_AGENT=ua)
        self.assertNotEqual(default.template_name[0], mobile.template_name[0])

    def test_blog_views(self):
        """
        Basic status code test for blog views.
        """
        response = self.client.get(reverse("blog_post_list"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("blog_post_feed", args=("rss",)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("blog_post_feed", args=("atom",)))
        self.assertEqual(response.status_code, 200)
        blog_post = BlogPost.objects.create(title="Post", user=self._user,
                                            status=CONTENT_STATUS_PUBLISHED)
        response = self.client.get(blog_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # Test the blog is login protected if its page has login_required
        # set to True.
        slug = settings.BLOG_SLUG or "/"
        RichTextPage.objects.create(title="blog", slug=slug,
                                    login_required=True)
        response = self.client.get(reverse("blog_post_list"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.redirect_chain) > 0)
        redirect_path = urlparse(response.redirect_chain[0][0]).path
        self.assertEqual(redirect_path, settings.LOGIN_URL)

    def test_rating(self):
        """
        Test that ratings can be posted and avarage/count are calculated.
        """
        blog_post = BlogPost.objects.create(title="Ratings", user=self._user,
                                            status=CONTENT_STATUS_PUBLISHED)
        data = RatingForm(blog_post).initial
        for value in RATING_RANGE:
            data["value"] = value
            response = self.client.post(reverse("rating"), data=data)
            response.delete_cookie("mezzanine-rating")
        blog_post = BlogPost.objects.get(id=blog_post.id)
        count = len(RATING_RANGE)
        average = sum(RATING_RANGE) / float(count)
        self.assertEqual(blog_post.rating_count, count)
        self.assertEqual(blog_post.rating_average, average)

    def queries_used_for_template(self, template, **context):
        """
        Return the number of queries used when rendering a template
        string.
        """
        connection.queries = []
        t = Template(template)
        t.render(Context(context))
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

    def test_comment_queries(self):
        """
        Test that rendering comments executes the same number of
        queries, regardless of the number of nested replies.
        """
        blog_post = BlogPost.objects.create(title="Post", user=self._user)
        content_type = ContentType.objects.get_for_model(blog_post)
        kwargs = {"content_type": content_type, "object_pk": blog_post.id,
                  "site_id": settings.SITE_ID}
        template = "{% load comment_tags %}{% comment_thread blog_post %}"
        context = {
            "blog_post": blog_post,
            "posted_comment_form": None,
            "unposted_comment_form": None,
        }
        before = self.queries_used_for_template(template, **context)
        self.assertTrue(before > 0)
        self.create_recursive_objects(ThreadedComment, "replied_to", **kwargs)
        after = self.queries_used_for_template(template, **context)
        self.assertEquals(before, after)

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
        self.assertEquals(before, after)

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
                title="Page for %s" % unicode(label),
                status=CONTENT_STATUS_PUBLISHED))
            template += "{%% page_menu '%s' %%}" % path
        rendered = Template(template).render(Context({}))
        for page in pages:
            self.assertEquals(rendered.count(page.title), len(page.in_menus))

    def test_keywords(self):
        """
        Test that the keywords_string field is correctly populated.
        """
        page = RichTextPage.objects.create(title="test keywords")
        keywords = set(["how", "now", "brown", "cow"])
        Keyword.objects.all().delete()
        for keyword in keywords:
            keyword_id = Keyword.objects.get_or_create(title=keyword)[0].id
            page.keywords.add(AssignedKeyword(keyword_id=keyword_id))
        page = RichTextPage.objects.get(id=page.id)
        self.assertEquals(keywords, set(page.keywords_string.split()))
        # Test removal.
        first = Keyword.objects.all()[0]
        keywords.remove(first.title)
        first.delete()
        page = RichTextPage.objects.get(id=page.id)
        self.assertEquals(keywords, set(page.keywords_string.split()))
        page.delete()

    def test_search(self):
        """
        Test search.
        """
        RichTextPage.objects.all().delete()
        published = {"status": CONTENT_STATUS_PUBLISHED}
        first = RichTextPage.objects.create(title="test page",
                                           status=CONTENT_STATUS_DRAFT).id
        second = RichTextPage.objects.create(title="test another test page",
                                            **published).id
        # Draft shouldn't be a result.
        results = RichTextPage.objects.search("test")
        self.assertEqual(len(results), 1)
        RichTextPage.objects.filter(id=first).update(**published)
        results = RichTextPage.objects.search("test")
        self.assertEqual(len(results), 2)
        # Either word.
        results = RichTextPage.objects.search("another test")
        self.assertEqual(len(results), 2)
        # Must include first word.
        results = RichTextPage.objects.search("+another test")
        self.assertEqual(len(results), 1)
        # Mustn't include first word.
        results = RichTextPage.objects.search("-another test")
        self.assertEqual(len(results), 1)
        if results:
            self.assertEqual(results[0].id, first)
        # Exact phrase.
        results = RichTextPage.objects.search('"another test"')
        self.assertEqual(len(results), 1)
        if results:
            self.assertEqual(results[0].id, second)
        # Test ordering.
        results = RichTextPage.objects.search("test")
        self.assertEqual(len(results), 2)
        if results:
            self.assertEqual(results[0].id, second)

    def test_forms(self):
        """
        Simple 200 status check against rendering and posting to forms
        with both optional and required fields.
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
        Test that an editable setting can be overridden with a DB
        value and that the data type is preserved when the value is
        returned back out of the DB. Also checks to ensure no
        unsupported types are defined for editable settings.
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
                setting = "%s: %s" % (setting_name, setting_type)
                self.fail("Unsupported setting type for %s" % setting)
            values_by_name[setting_name] = setting_value
            Setting.objects.create(name=setting_name, value=str(setting_value))
        # Load the settings and make sure the DB values have persisted.
        settings.use_editable()
        for (name, value) in values_by_name.items():
            self.assertEqual(getattr(settings, name), value)

    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        warnings = []
        warnings.extend(run_pyflakes_for_package("mezzanine"))
        warnings.extend(run_pep8_for_package("mezzanine"))
        if warnings:
            self.fail("Syntax warnings!\n\n%s" % "\n".join(warnings))

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

    def _create_page(self, title, status):
        return RichTextPage.objects.create(title=title, status=status)

    def _test_site_pages(self, title, status, count):
        # test _default_manager
        pages = RichTextPage._default_manager.all()
        self.assertEqual(pages.count(), count)
        self.assertTrue(title in [page.title for page in pages])

        # test objects manager
        pages = RichTextPage.objects.all()
        self.assertEqual(pages.count(), count)
        self.assertTrue(title in [page.title for page in pages])

        # test response status code
        code = 200 if status == CONTENT_STATUS_PUBLISHED else 404
        pages = RichTextPage.objects.filter(status=status)
        response = self.client.get(pages[0].get_absolute_url())
        self.assertEqual(response.status_code, code)

    def test_mulisite(self):
        from django.conf import settings

        # setup
        try:
            old_site_id = settings.SITE_ID
        except:
            old_site_id = None

        site1 = Site.objects.create(domain="site1.com")
        site2 = Site.objects.create(domain="site2.com")

        # create pages under site1, which should be only accessible
        # when SITE_ID is site1
        settings.SITE_ID = site1.pk
        site1_page = self._create_page("Site1", CONTENT_STATUS_PUBLISHED)
        self._test_site_pages("Site1", CONTENT_STATUS_PUBLISHED, count=1)

        # create pages under site2, which should only be accessible
        # when SITE_ID is site2
        settings.SITE_ID = site2.pk
        self._create_page("Site2", CONTENT_STATUS_PUBLISHED)
        self._test_site_pages("Site2", CONTENT_STATUS_PUBLISHED, count=1)

        # original page should 404
        response = self.client.get(site1_page.get_absolute_url())
        self.assertEqual(response.status_code, 404)

        # change back to site1, and only the site1 pages should be retrieved
        settings.SITE_ID = site1.pk
        self._test_site_pages("Site1", CONTENT_STATUS_PUBLISHED, count=1)

        # insert a new record, see the count change
        self._create_page("Site1 Draft", CONTENT_STATUS_DRAFT)
        self._test_site_pages("Site1 Draft", CONTENT_STATUS_DRAFT, count=2)
        self._test_site_pages("Site1 Draft", CONTENT_STATUS_PUBLISHED, count=2)

        # change back to site2, and only the site2 pages should be retrieved
        settings.SITE_ID = site2.pk
        self._test_site_pages("Site2", CONTENT_STATUS_PUBLISHED, count=1)

        # insert a new record, see the count change
        self._create_page("Site2 Draft", CONTENT_STATUS_DRAFT)
        self._test_site_pages("Site2 Draft", CONTENT_STATUS_DRAFT, count=2)
        self._test_site_pages("Site2 Draft", CONTENT_STATUS_PUBLISHED, count=2)

        # tear down
        if old_site_id:
            settings.SITE_ID = old_site_id
        else:
            del settings.SITE_ID

        site1.delete()
        site2.delete()

    def test_gallery_import(self):
        """
        Test that a gallery creates images when given a zip file to
        import, and that descriptions are created.
        """
        zip_name = "gallery.zip"
        copy_test_to_media("mezzanine.core", zip_name)
        title = str(uuid4())
        gallery = Gallery.objects.create(title=title, zip_import=zip_name)
        images = list(gallery.images.all())
        self.assertTrue(images)
        self.assertTrue(all([image.description for image in images]))
        # Clean up.
        rmtree(unicode(os.path.join(settings.MEDIA_ROOT,
                                    GALLERIES_UPLOAD_DIR, title)))

    def test_thumbnail_generation(self):
        """
        Test that a thumbnail is created and resized.
        """
        image_name = "image.jpg"
        size = (24, 24)
        copy_test_to_media("mezzanine.core", image_name)
        thumb_name = os.path.join(settings.THUMBNAILS_DIR_NAME,
                                  image_name.replace(".", "-%sx%s." % size))
        thumb_path = os.path.join(settings.MEDIA_ROOT, thumb_name)
        thumb_image = thumbnail(image_name, *size)
        self.assertEqual(os.path.normpath(thumb_image.lstrip("/")), thumb_name)
        self.assertNotEqual(os.path.getsize(thumb_path), 0)
        thumb = Image.open(thumb_path)
        self.assertEqual(thumb.size, size)
        # Clean up.
        del thumb
        os.remove(os.path.join(settings.MEDIA_ROOT, image_name))
        os.remove(os.path.join(thumb_path))
        rmtree(os.path.join(os.path.dirname(thumb_path)))
