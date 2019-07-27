from modeltranslation.translator import translator, TranslationOptions
from mezzanine.core.translation import TranslatedRichText
from mezzanine.forms import get_form_model, get_field_model


Form = get_form_model()
Field = get_field_model()


class TranslatedForm(TranslatedRichText):
    fields = ('button_text', 'response', 'email_subject', 'email_message',)


class TranslatedField(TranslationOptions):
    fields = ('label', 'choices', 'default', 'placeholder_text', 'help_text',)


translator.register(Form, TranslatedForm)
translator.register(Field, TranslatedField)
