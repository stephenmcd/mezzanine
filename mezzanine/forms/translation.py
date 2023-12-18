from modeltranslation.translator import TranslationOptions, translator

from mezzanine.core.translation import TranslatedRichText
from mezzanine.forms.models import Field, Form


class TranslatedForm(TranslatedRichText):
    fields = (
        "button_text",
        "response",
        "email_subject",
        "email_message",
    )


class TranslatedField(TranslationOptions):
    fields = (
        "label",
        "choices",
        "default",
        "placeholder_text",
        "help_text",
    )


translator.register(Form, TranslatedForm)
translator.register(Field, TranslatedField)
