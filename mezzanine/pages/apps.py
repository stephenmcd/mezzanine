from django.apps import AppConfig
from django.core.checks import register

from .checks import check_context_processor


class PagesConfig(AppConfig):

    name = 'mezzanine.pages'

    def ready(self):
        register()(check_context_processor)
