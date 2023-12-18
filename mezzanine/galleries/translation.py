from modeltranslation.translator import TranslationOptions, translator

from mezzanine.core.translation import TranslatedRichText
from mezzanine.galleries.models import Gallery, GalleryImage


class TranslatedGallery(TranslatedRichText):
    fields = ()


class TranslatedGalleryImage(TranslationOptions):
    fields = ("description",)


translator.register(Gallery, TranslatedGallery)
translator.register(GalleryImage, TranslatedGalleryImage)
