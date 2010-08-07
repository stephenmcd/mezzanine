
from django.db.models import TextField


class HtmlField(TextField):
    """
    TextField that stores HTML.
    """

    def formfield(self, **kwargs):
        """
        Apply the class to the widget that will render the field as a
        TincyMCE Editor.
        """
        formfield = super(HtmlField, self).formfield(**kwargs)
        formfield.widget.attrs["class"] = "mceEditor"
        return formfield
