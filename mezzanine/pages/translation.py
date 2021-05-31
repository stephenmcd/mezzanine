from modeltranslation.translator import TranslationOptions, translator

from mezzanine.core.translation import TranslatedDisplayable, TranslatedRichText
from mezzanine.pages.models import Link, Page, RichTextPage


class TranslatedPage(TranslatedDisplayable):
    fields = ("titles",)


class TranslatedRichTextPage(TranslatedRichText):
    fields = ()


class TranslatedLink(TranslationOptions):
    fields = ()


translator.register(Page, TranslatedPage)
translator.register(RichTextPage, TranslatedRichTextPage)
translator.register(Link, TranslatedLink)
