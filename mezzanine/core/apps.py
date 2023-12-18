from django.apps import AppConfig


class CoreConfig(AppConfig):

    name = "mezzanine.core"

    def ready(self):
        from . import checks  # noqa
