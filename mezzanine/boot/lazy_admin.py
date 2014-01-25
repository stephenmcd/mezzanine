from __future__ import unicode_literals

from django.conf.urls import patterns, include
from django.contrib.admin.sites import AdminSite
from filebrowser.sites import site as filebrowser_site


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
            urls += patterns("",
                ("^media-library/", include(filebrowser_site.urls)),
            )
        return urls
