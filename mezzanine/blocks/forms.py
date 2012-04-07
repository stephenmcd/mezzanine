from django.forms import ModelForm
from mezzanine.blocks.models import Block, RichTextBlock

class BlockForm(ModelForm):
    class Meta:
        model = Block
        exclude = ('slug', )

class RichTextBlock(ModelForm):
    class Meta:
        model = RichTextBlock
        exclude = ('slug', )
