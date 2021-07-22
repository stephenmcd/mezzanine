from django.apps import AppConfig


class TwitterConfig(AppConfig):

    name = "mezzanine.twitter"

    def ready(self):
        from . import checks  # noqa
