from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib.admin.sites import AdminSite

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
        for name, deferred_args, deferred_kwargs in self._deferred:
            getattr(AdminSite, name)(self, *deferred_args, **deferred_kwargs)

    @property
    def urls(self):
        from django.conf import settings
        urls = patterns("", ("", super(LazyAdminSite, self).urls),)
        # Filebrowser admin media library.
        fb_name = getattr(settings, "PACKAGE_NAME_FILEBROWSER", "")
        if fb_name in settings.INSTALLED_APPS:
            try:
                fb_urls = import_dotted_path("%s.sites.site" % fb_name).urls
            except ImportError:
                fb_urls = "%s.urls" % fb_name
            urls = patterns("", ("^media-library/", include(fb_urls)),) + urls
        # Give the urlpatterm for the user password change view an
        # actual name, so that it can be reversed with multiple
        # languages are supported in the admin.
        for admin in self._registry.values():
            user_change_password = getattr(admin, "user_change_password", None)
            if user_change_password:
                urls = patterns("",
                    url("^auth/user/(\d+)/password/$",
                        self.admin_view(user_change_password),
                        name="user_change_password"),
                ) + urls
                break
        return urls
