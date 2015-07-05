from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite, NotRegistered

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
        # Call register/unregister.
        for name, deferred_args, deferred_kwargs in self._deferred:
            getattr(AdminSite, name)(self, *deferred_args, **deferred_kwargs)

    @property
    def urls(self):
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
        User = get_user_model()
        for admin in self._registry.values():
            user_change_password = getattr(admin, "user_change_password", None)
            if user_change_password:
                bits = (User._meta.app_label, User._meta.object_name.lower())
                urls = patterns("",
                    url("^%s/%s/(\d+)/password/$" % bits,
                        self.admin_view(user_change_password),
                        name="user_change_password"),
                ) + urls
                break
        return urls
