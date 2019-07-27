from modeltranslation.translator import translator, TranslationOptions
from mezzanine.core.translation import (TranslatedDisplayable,
                                        TranslatedRichText)
from mezzanine.pages import get_page_model, get_rich_text_page_model
from mezzanine.pages import get_link_model


Page = get_page_model()
RichTextPage = get_rich_text_page_model()
Link = get_link_model()


class TranslatedPage(TranslatedDisplayable):
    fields = ('titles',)


class TranslatedRichTextPage(TranslatedRichText):
    fields = ()


class TranslatedLink(TranslationOptions):
    fields = ()


translator.register(Page, TranslatedPage)
translator.register(RichTextPage, TranslatedRichTextPage)
translator.register(Link, TranslatedLink)
