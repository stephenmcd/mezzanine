from django.apps import AppConfig


class PagesConfig(AppConfig):

    name = 'mezzanine.pages'

    def ready(self):
        from . import checks  # noqa
