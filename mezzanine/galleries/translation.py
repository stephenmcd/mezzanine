from modeltranslation.translator import translator, TranslationOptions
from mezzanine.core.translation import TranslatedRichText
from mezzanine.galleries.models import GalleryImage, Gallery


class TranslatedGallery(TranslatedRichText):
    fields = ()


class TranslatedGalleryImage(TranslationOptions):
    fields = ('description',)

translator.register(Gallery, TranslatedGallery)
translator.register(GalleryImage, TranslatedGalleryImage)
