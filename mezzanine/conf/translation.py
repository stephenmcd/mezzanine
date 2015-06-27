from modeltranslation.translator import translator, TranslationOptions
from mezzanine.conf.models import Setting


class TranslatedSetting(TranslationOptions):
    fields = ('value',)

translator.register(Setting, TranslatedSetting)
