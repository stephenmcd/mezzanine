from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import (AdminSite, site as default_site,
    NotRegistered, AlreadyRegistered)
from django.shortcuts import redirect

from mezzanine.utils.importing import import_dotted_path


class LazyAdminSite(AdminSite):
    """
    Defers calls to register/unregister until autodiscover is called
    to avoid load issues with injectable model fields defined by
    ``settings.EXTRA_MODEL_FIELDS``.
    """

    def __init__(self, *args, **kwargs):
        self._deferred = []
        super(LazyAdminSite, self).__init__(*args, **kwargs)

    def register(self, *args, **kwargs):
        for name, deferred_args, deferred_kwargs in self._deferred:
            if name == "unregister" and deferred_args[0] == args[0]:
                self._deferred.append(("register", args, kwargs))
                break
        else:
            super(LazyAdminSite, self).register(*args, **kwargs)

    def unregister(self, *args, **kwargs):
        self._deferred.append(("unregister", args, kwargs))

    def lazy_registration(self):
        # First, directly handle models we don't want at all,
        # as per the ``ADMIN_REMOVAL`` setting.
        for model in getattr(settings, "ADMIN_REMOVAL", []):
            try:
                model = tuple(model.rsplit(".", 1))
                exec("from %s import %s" % model)
            except ImportError:
                pass
            else:
                try:
                    AdminSite.unregister(self, eval(model[1]))
                except NotRegistered:
                    pass
        # Pick up any admin classes registered via decorator to the
        # default admin site.
        for model, admin in default_site._registry.items():
            self._deferred.append(("register", (model, admin.__class__), {}))
        # Call register/unregister.
        for name, args, kwargs in self._deferred:
            try:
                getattr(AdminSite, name)(self, *args, **kwargs)
            except (AlreadyRegistered, NotRegistered):
                pass

    @property
    def urls(self):
        urls = [url("", super(LazyAdminSite, self).urls)]

        # Filebrowser admin media library.
        fb_name = getattr(settings, "PACKAGE_NAME_FILEBROWSER", "")
        if fb_name in settings.INSTALLED_APPS:
            try:
                fb_urls = import_dotted_path("%s.sites.site" % fb_name).urls
            except ImportError:
                fb_urls = "%s.urls" % fb_name
            urls = [
                # This gives the media library a root URL (which filebrowser
                # doesn't provide), so that we can target it in the
                # ADMIN_MENU_ORDER setting, allowing each view to correctly
                # highlight its left-hand admin nav item.
                url("^media-library/$", lambda r: redirect("fb_browse"),
                    name="media-library"),
                url("^media-library/", include(fb_urls)),
            ] + urls

        # Give the urlpattern for the user password change view an
        # actual name, so that it can be reversed with multiple
        # languages are supported in the admin.
        User = get_user_model()
        for admin in self._registry.values():
            user_change_password = getattr(admin, "user_change_password", None)
            if user_change_password:
                bits = (User._meta.app_label, User._meta.object_name.lower())
                urls = [
                    url("^%s/%s/(\d+)/password/$" % bits,
                        self.admin_view(user_change_password),
                        name="user_change_password"),
                ] + urls
                break

        # Misc Mezzanine urlpatterns that should reside under /admin/ url,
        # specifically for compatibility with SSLRedirectMiddleware.
        from mezzanine.core.views import displayable_links_js, static_proxy
        from mezzanine.generic.views import admin_keywords_submit
        urls += [
            url("^admin_keywords_submit/$", admin_keywords_submit,
                name="admin_keywords_submit"),
            url("^asset_proxy/$", static_proxy, name="static_proxy"),
            url("^displayable_links.js$", displayable_links_js,
                name="displayable_links_js"),
        ]
        if "mezzanine.pages" in settings.INSTALLED_APPS:
            from mezzanine.pages.views import admin_page_ordering
            urls.append(url("^admin_page_ordering/$", admin_page_ordering,
                            name="admin_page_ordering"))

        return urls
