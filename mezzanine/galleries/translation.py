from modeltranslation.translator import translator, TranslationOptions
from mezzanine.core.translation import TranslatedRichText
from mezzanine.galleries import get_gallery_model, get_gallery_image_model


Gallery = get_gallery_model()
GalleryImage = get_gallery_image_model()


class TranslatedGallery(TranslatedRichText):
    fields = ()


class TranslatedGalleryImage(TranslationOptions):
    fields = ('description',)


translator.register(Gallery, TranslatedGallery)
translator.register(GalleryImage, TranslatedGalleryImage)
