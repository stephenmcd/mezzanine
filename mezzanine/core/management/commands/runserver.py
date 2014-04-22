
import os

from django.conf import settings
from django.contrib.staticfiles.management.commands import runserver
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.http import Http404
from django.views.static import serve


class MezzStaticFilesHandler(StaticFilesHandler):

    def _should_handle(self, path):
        return path.startswith(self.base_url[2])

    def get_response(self, request):
        response = super(MezzStaticFilesHandler, self).get_response(request)
        if response.status_code == 404:
            path = self.file_path(request.path).replace(os.sep, "/")
            try:
                return serve(request, path, document_root=settings.STATIC_ROOT)
            except Http404:
                # Just return the original 404 response.
                pass
        return response


class Command(runserver.Command):
    """
    Overrides runserver so that we can serve uploaded files
    during development, and not require every single developer on
    every single one of their projects to have to set up multiple
    web server aliases for serving static content.
    See https://code.djangoproject.com/ticket/15199

    For ease, we also serve any static files that have been stored
    under the project's ``STATIC_ROOT``.
    """

    def get_handler(self, *args, **options):
        handler = super(Command, self).get_handler(*args, **options)
        if settings.DEBUG or options["insecure_serving"]:
            handler = MezzStaticFilesHandler(handler)
        return handler
