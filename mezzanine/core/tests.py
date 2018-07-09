from __future__ import unicode_literals

import re
import pytz
from unittest import skipUnless

from mezzanine.core.middleware import FetchFromCacheMiddleware
from mezzanine.core.templatetags.mezzanine_tags import initialize_nevercache
from mezzanine.utils.cache import cache_installed
from mezzanine.utils.sites import current_site_id, override_current_site_id
from mezzanine.utils.urls import admin_url

try:
    # Python 3
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib import urlencode

from django.conf.urls import url
from django.contrib.admin import AdminSite
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.sites.models import Site
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.management import call_command, CommandError
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import Textarea
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.templatetags.static import static
from django.test.utils import override_settings
from django.utils.html import strip_tags
from django.utils.timezone import datetime, now, timedelta

from mezzanine.conf import settings
from mezzanine.core.admin import BaseDynamicInlineAdmin
from mezzanine.core.fields import RichTextField, MultiChoiceField
from mezzanine.core.managers import DisplayableManager
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED)
from mezzanine.forms.admin import FieldAdmin
from mezzanine.forms.models import Form
from mezzanine.pages.models import Page, RichTextPage
from mezzanine.utils.deprecation import (get_middleware_setting,
                                         get_middleware_setting_name)
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.tests import (TestCase, run_pyflakes_for_package,
                                             run_pep8_for_package)
from mezzanine.utils.html import TagCloser


class CoreTests(TestCase):

    def test_tagcloser(self):
        """
        Test tags are closed, and tags that shouldn't be closed aren't.
        """
        self.assertEqual(TagCloser("<p>Unclosed paragraph").html,
                         "<p>Unclosed paragraph</p>")

        self.assertEqual(TagCloser("Line break<br>").html,
                         "Line break<br>")

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

    @skipUnless("mezzanine.pages" in settings.INSTALLED_APPS,
                "pages app required")
    def test_description(self):
        """
        Test generated description is text version of the first line
        of content.
        """
        description = "<p>How now brown cow</p>"
        page = RichTextPage.objects.create(title="Draft",
                                           content=description * 3)
        self.assertEqual(page.description, strip_tags(description))

    @skipUnless("mezzanine.pages" in settings.INSTALLED_APPS,
                "pages app required")
    def test_draft(self):
        """
        Test a draft object as only being viewable by a staff member.
        """
        self.client.logout()
        draft = RichTextPage.objects.create(title="Draft",
                                            status=CONTENT_STATUS_DRAFT)
        response = self.client.get(draft.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 404)
        self.client.login(username=self._username, password=self._password)
        response = self.client.get(draft.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_searchable_manager_search_fields(self):
        """
        Test that SearchableManager can get appropriate params.
        """
        manager = DisplayableManager()
        self.assertFalse(manager._search_fields)
        manager = DisplayableManager(search_fields={'foo': 10})
        self.assertTrue(manager._search_fields)

    @skipUnless("mezzanine.pages" in settings.INSTALLED_APPS,
                "pages app required")
    def test_search(self):
        """
        Objects with status "Draft" should not be within search results.
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

        # Test ordering without age scaling.
        settings.SEARCH_AGE_SCALE_FACTOR = 0
        RichTextPage.objects.filter(id=first).update(
            publish_date=datetime(2017, 1, 1, tzinfo=pytz.utc))
        RichTextPage.objects.filter(id=second).update(
            publish_date=datetime(2016, 1, 1, tzinfo=pytz.utc))
        results = RichTextPage.objects.search("test")
        self.assertEqual(len(results), 2)
        if results:
            self.assertEqual(results[0].id, second)

        # Test ordering with age scaling.
        settings.SEARCH_AGE_SCALE_FACTOR = 1.5
        results = RichTextPage.objects.search("test")
        self.assertEqual(len(results), 2)
        if results:
            # `first` should now be ranked higher.
            self.assertEqual(results[0].id, first)

        # Test results that have a publish date in the future
        future = RichTextPage.objects.create(
            title="test page to be published in the future",
            publish_date=now() + timedelta(days=10),
            **published
        ).id
        results = RichTextPage.objects.search("test", for_user=self._username)
        self.assertEqual(len(results), 3)
        if results:
            self.assertEqual(results[0].id, future)

        # Test the actual search view.
        response = self.client.get(reverse("search") + "?q=test")
        self.assertEqual(response.status_code, 200)

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
        response = self.client.get(pages[0].get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, code)

    @skipUnless("mezzanine.pages" in settings.INSTALLED_APPS,
                "pages app required")
    def test_multisite(self):
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
        response = self.client.get(site1_page.get_absolute_url(), follow=True)
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

    def _static_proxy(self, querystring):
        self.client.login(username=self._username, password=self._password)
        proxy_url = '%s?%s' % (reverse('static_proxy'), querystring)
        response = self.client.get(proxy_url)
        self.assertEqual(response.status_code, 200)

    @override_settings(STATIC_URL='/static/')
    def test_static_proxy(self):
        querystring = urlencode([('u', static("test/image.jpg"))])
        self._static_proxy(querystring)

    @override_settings(STATIC_URL='http://testserver/static/')
    def test_static_proxy_with_host(self):
        querystring = urlencode(
            [('u', static("test/image.jpg"))])
        self._static_proxy(querystring)

    @override_settings(STATIC_URL='http://testserver:8000/static/')
    def test_static_proxy_with_static_url_with_full_host(self):
        from django.templatetags.static import static
        querystring = urlencode([('u', static("test/image.jpg"))])
        self._static_proxy(querystring)

    def _get_csrftoken(self, response):
        csrf = re.findall(
            b'\<input type\=\'hidden\' name\=\'csrfmiddlewaretoken\' '
            b'value\=\'([^"\']+)\' \/\>',
            response.content
        )
        self.assertEqual(len(csrf), 1, 'No csrfmiddlewaretoken found!')
        return csrf[0]

    def _get_formurl(self, response):
        action = re.findall(
            b'\<form action\=\"([^\"]*)\" method\=\"post\"\>',
            response.content
        )
        self.assertEqual(len(action), 1, 'No form with action found!')
        if action[0] == b'':
            action = response.request['PATH_INFO']
        return action

    @skipUnless('mezzanine.pages' in settings.INSTALLED_APPS,
                'pages app required')
    @override_settings(LANGUAGE_CODE="en")
    def test_password_reset(self):
        """
        Test sending of password-reset mails and evaluation of the links.
        """
        self.client.logout()
        del mail.outbox[:]

        # Go to admin-login, search for reset-link
        response = self.client.get('/admin/', follow=True)
        self.assertContains(response, u'Forgot password?')
        url = re.findall(
            b'\<a href\=["\']([^\'"]+)["\']\>Forgot password\?\<\/a\>',
            response.content
        )
        self.assertEqual(len(url), 1)
        url = url[0]

        # Go to reset-page, submit form
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        csrf = self._get_csrftoken(response)
        url = self._get_formurl(response)

        response = self.client.post(url, {
            'csrfmiddlewaretoken': csrf,
            'email': self._emailaddress
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        # Get reset-link, submit form
        url = re.findall(
            r'http://example.com((?:/\w{2,3})?/reset/[^/]+/[^/]+/)',
            mail.outbox[0].body
        )[0]
        response = self.client.get(url)
        csrf = self._get_csrftoken(response)
        url = self._get_formurl(response)
        response = self.client.post(url, {
            'csrfmiddlewaretoken': csrf,
            'new_password1': 'newdefault',
            'new_password2': 'newdefault'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_richtext_widget(self):
        """
        Test that the RichTextField gets its widget type correctly from
        settings, and is able to be overridden in a form's Meta.
        """

        class RichTextModel(models.Model):
            text_default = RichTextField()
            text_overridden = RichTextField()

        form_class = modelform_factory(
            RichTextModel,
            fields=('text_default', 'text_overridden'),
            widgets={'text_overridden': Textarea})
        form = form_class()

        richtext_widget = import_dotted_path(settings.RICHTEXT_WIDGET_CLASS)

        self.assertIsInstance(form.fields['text_default'].widget,
                              richtext_widget)
        self.assertIsInstance(form.fields['text_overridden'].widget,
                              Textarea)

    def test_admin_sites_dropdown(self):
        """
        Ensures the site selection dropdown appears in the admin.
        """
        self.client.login(username=self._username, password=self._password)
        response = self.client.get('/admin/', follow=True)
        set_site_url = reverse("set_site")
        # Set site URL shouldn't appear without multiple sites.
        self.assertNotContains(response, set_site_url)
        site1 = Site.objects.create(domain="test-site-dropdown1.com",
                                    name="test-site-dropdown1.com")
        site2 = Site.objects.create(domain="test-site-dropdown2.com",
                                    name="test-site-dropdown2.com")
        response = self.client.get('/admin/', follow=True)
        self.assertContains(response, set_site_url)
        self.assertContains(response, site1.name)
        self.assertContains(response, site2.name)
        site1.delete()
        site2.delete()

    def test_dynamic_inline_admins(self):
        """
        Verifies that ``BaseDynamicInlineAdmin`` properly adds the ``_order``
        field for admins of ``Orderable`` subclasses.
        """
        request = self._request_factory.get('/admin/')
        request.user = self._user
        field_admin = FieldAdmin(Form, AdminSite())
        fieldsets = field_admin.get_fieldsets(request)
        self.assertEqual(fieldsets[0][1]['fields'][-1], '_order')
        fields = field_admin.get_fields(request)
        self.assertEqual(fields[-1], '_order')

    def test_dynamic_inline_admins_fields_tuple(self):
        """
        Checks if moving the ``_order`` field works with immutable sequences.
        """
        class MyModelInline(BaseDynamicInlineAdmin, InlineModelAdmin):
            # Any model would work since we're only instantiating the class and
            # not actually using it.
            model = RichTextPage
            fields = ('a', '_order', 'b')

        request = self._request_factory.get('/admin/')
        inline = MyModelInline(None, AdminSite())
        fields = inline.get_fieldsets(request)[0][1]['fields']
        self.assertSequenceEqual(fields, ('a', 'b', '_order'))

    def test_dynamic_inline_admins_fields_without_order(self):
        """
        Checks that ``_order`` field will be added if ``fields`` are listed
        without it.
        """
        class MyModelInline(BaseDynamicInlineAdmin, InlineModelAdmin):
            model = RichTextPage
            fields = ('a', 'b')

        request = self._request_factory.get('/admin/')
        inline = MyModelInline(None, AdminSite())
        fields = inline.get_fieldsets(request)[0][1]['fields']
        self.assertSequenceEqual(fields, ('a', 'b', '_order'))

    def test_dynamic_inline_admins_fieldsets(self):
        """
        Tests if ``_order`` is moved to the end of the last fieldsets fields.
        """
        class MyModelInline(BaseDynamicInlineAdmin, InlineModelAdmin):
            model = RichTextPage
            fieldsets = (("Fieldset 1", {'fields': ('a',)}),
                         ("Fieldset 2", {'fields': ('_order', 'b')}),
                         ("Fieldset 3", {'fields': ('c')}))

        request = self._request_factory.get('/admin/')
        inline = MyModelInline(None, AdminSite())
        fieldsets = inline.get_fieldsets(request)
        self.assertEqual(fieldsets[-1][1]["fields"][-1], '_order')
        self.assertNotIn('_order', fieldsets[1][1]["fields"])

    def test_cache_installed(self):

        test_contexts = [
            (False,
             ['mezzanine.core.middleware.FetchFromCacheMiddleware']),
            (True,
             ['mezzanine.core.middleware.UpdateCacheMiddleware',
              'mezzanine.core.tests.SubclassMiddleware']),
            (True,
             ['mezzanine.core.middleware.UpdateCacheMiddleware',
              'mezzanine.core.tests.FetchFromCacheMiddleware',
              'mezzanine.core.tests.function_middleware']),
            (True,
             ['mezzanine.core.middleware.UpdateCacheMiddleware',
              'mezzanine.core.middleware.FetchFromCacheMiddleware']),
        ]

        with self.settings(TESTING=False):  # Well, this is silly
            for expected_result, middlewares in test_contexts:
                kwargs = {get_middleware_setting_name(): middlewares}
                with self.settings(**kwargs):
                    cache_installed.cache_clear()
                    self.assertEqual(cache_installed(), expected_result)

        cache_installed.cache_clear()


class SubclassMiddleware(FetchFromCacheMiddleware):
    pass


def function_middleware(get_response):
    def middleware(request):
        return get_response(request)
    return middleware


@skipUnless("mezzanine.pages" in settings.INSTALLED_APPS,
            "pages app required")
class SiteRelatedTestCase(TestCase):

    def test_update_site(self):
        from django.conf import settings
        from mezzanine.utils.sites import current_site_id

        # setup
        try:
            old_site_id = settings.SITE_ID
        except:
            old_site_id = None

        site1 = Site.objects.create(domain="site1.com")
        site2 = Site.objects.create(domain="site2.com")

        # default behaviour, page gets assigned current site
        settings.SITE_ID = site2.pk
        self.assertEqual(settings.SITE_ID, current_site_id())
        page = RichTextPage()
        page.save()
        self.assertEqual(page.site_id, site2.pk)

        # Subsequent saves do not update site to current site
        page.site = site1
        page.save()
        self.assertEqual(page.site_id, site1.pk)

        # resave w/ update_site=True, page gets assigned current site
        settings.SITE_ID = site1.pk
        page.site = site2
        page.save(update_site=True)
        self.assertEqual(page.site_id, site1.pk)

        # resave w/ update_site=False, page does not update site
        settings.SITE_ID = site2.pk
        page.save(update_site=False)
        self.assertEqual(page.site_id, site1.pk)

        # When update_site=True, new page gets assigned current site
        settings.SITE_ID = site2.pk
        page = RichTextPage()
        page.site = site1
        page.save(update_site=True)
        self.assertEqual(page.site_id, site2.pk)

        # When update_site=False, new page keeps current site
        settings.SITE_ID = site2.pk
        page = RichTextPage()
        page.site = site1
        page.save(update_site=False)
        self.assertEqual(page.site_id, site1.pk)

        # When site explicitly assigned, new page keeps assigned site
        settings.SITE_ID = site2.pk
        page = RichTextPage()
        page.site = site1
        page.save()
        self.assertEqual(page.site_id, site1.pk)

        # tear down
        if old_site_id:
            settings.SITE_ID = old_site_id
        else:
            del settings.SITE_ID

        site1.delete()
        site2.delete()

    def test_override_site_id(self):
        self.assertEqual(current_site_id(), 1)
        with override_current_site_id(2):
            self.assertEqual(current_site_id(), 2)
        self.assertEqual(current_site_id(), 1)


class CSRFTestViews(object):
    def nevercache_view(request):
        template = "{% load mezzanine_tags %}"
        template += "{% nevercache %}"
        template += "{% csrf_token %}"
        template += "{% endnevercache %}"

        rendered = Template(template).render(RequestContext(request))

        return HttpResponse(rendered)

    urlpatterns = [
        url("^nevercache_view/", nevercache_view),
    ]


class CSRFTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        # Initialize nevercache again now that @override_settings is finished
        cache_installed.cache_clear()
        initialize_nevercache()

    @override_settings(**{
        "ROOT_URLCONF": CSRFTestViews,
        "CACHES": {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
             }
        },
        get_middleware_setting_name(): (
            'mezzanine.core.middleware.UpdateCacheMiddleware',) +
            get_middleware_setting() +
            ('mezzanine.core.middleware.FetchFromCacheMiddleware',
        ),
        "TESTING": False})
    def test_csrf_cookie_with_nevercache(self):
        """
        Test that the CSRF cookie is properly set when using nevercache.
        """

        # Clear the cached value for cache_installed and initialize nevercache
        cache_installed.cache_clear()
        initialize_nevercache()

        # Test uses an authenticated user as the middleware behavior differs
        self.client.login(username=self._username, password=self._password)
        response = self.client.get("/nevercache_view/")

        # CSRF token is expected to be rendered
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

        # The CSRF cookie should be present
        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        self.assertNotEqual(csrf_cookie, False)


class DisplayableTestCase(TestCase):
    def test_published(self):
        page = Page.objects.create(publish_date=None, expiry_date=None,
                                   status=CONTENT_STATUS_DRAFT)
        self.assertFalse(page.published())

        page.status = CONTENT_STATUS_PUBLISHED
        self.assertTrue(page.published())

        page.publish_date = now() + timedelta(days=10)
        self.assertFalse(page.published())

        page.publish_date = now() - timedelta(days=10)
        page.expiry_date = now() + timedelta(days=10)
        self.assertTrue(page.published())

        page.expiry_date = now() - timedelta(days=10)
        self.assertFalse(page.published())


class ContentTypedTestCase(TestCase):

    def test_set_content_model_base_concrete_class(self):
        page = Page.objects.create()
        page.set_content_model()
        self.assertEqual(page.content_model, None)
        self.assertIs(page.get_content_model(), page)

    def test_set_content_model_subclass(self):
        richtextpage = RichTextPage.objects.create()
        richtextpage.set_content_model()
        page = Page.objects.get(pk=richtextpage.pk)
        self.assertEqual(page.content_model, 'richtextpage')
        self.assertEqual(page.get_content_model(), richtextpage)

    def test_set_content_model_again(self):
        """
        Content model cannot change after initial save.

        That's the only time we'll know for certain that the __class__ is the
        lowest class in the hierarchy. Of course, content_model will keep
        getting set to None for base concrete classes, which is confusing but
        not necessarily a problem.
        """
        richtextpage = RichTextPage.objects.create()
        richtextpage.set_content_model()
        page = Page.objects.get(pk=richtextpage.pk)
        self.assertEqual(page.content_model, 'richtextpage')
        self.assertEqual(page.get_content_model(), richtextpage)
        page.set_content_model()
        self.assertEqual(page.content_model, 'richtextpage')
        self.assertEqual(page.get_content_model(), richtextpage)

    def test_contenttyped_admin_redirects(self):
        self.client.login(username=self._username, password=self._password)

        # Unsubclassed objects should not redirect
        page = Page.objects.create(title="Test page")
        response = self.client.get(admin_url(Page, "change", page.pk))
        self.assertEqual(response.status_code, 200)

        # Subclassed objects should redirect to the admin for child class
        richtext = RichTextPage.objects.create(title="Test rich text")
        response = self.client.get(admin_url(Page, "change", richtext.pk))
        richtext_change_url = admin_url(RichTextPage, "change", richtext.pk)
        self.assertRedirects(response, richtext_change_url)


class FieldsTestCase(TestCase):
    def test_multichoicefield_validate_valid(self):
        field = MultiChoiceField(choices=[('valid choice',)])
        field.validate(['valid choice'], None)

    def test_multichoicefield_validate_invalid(self):
        field = MultiChoiceField(choices=[('valid choice',)])
        with self.assertRaises(ValidationError):
            field.validate(['invalid choice'], None)


class CommandsTestCase(TestCase):
    def test_collect_templates(self):
        if hasattr(self, "assertRaisesRegex"):
            with self.assertRaisesRegex(
                    CommandError, 'Apps are not in INSTALLED_APPS: .*'):
                call_command('collecttemplates', 'nonexistent')
