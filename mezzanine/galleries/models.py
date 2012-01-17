
from cStringIO import StringIO
import os
import re
from zipfile import ZipFile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Orderable, RichText
from mezzanine.pages.models import Page
from mezzanine.utils.importing import import_dotted_path


class Gallery(Page, RichText):
    """
    Page bucket for gallery photos.
    """

    zip_import = models.FileField(upload_to="galleries", blank=True,
                    help_text=_("Upload a zip file containing images, and "
                                "they'll be imported into this gallery."))

    class Meta:
        verbose_name = _("Gallery")
        verbose_name_plural = _("Galleries")

    def save(self, *args, **kwargs):
        """
        If a zip file is uploaded, extract any images from it and add
        them to the gallery, before removing the zip file.
        """
        super(Gallery, self).save(*args, **kwargs)
        if self.zip_import:
            zip_file = ZipFile(self.zip_import.path)
            from PIL import Image
            for name in zip_file.namelist():
                data = zip_file.read(name)
                try:
                    image = Image.open(StringIO(data))
                    image.load()
                    image = Image.open(StringIO(data))
                    image.verify()
                except:
                    continue
                try:
                    dir_name = import_dotted_path("%s.settings" %
                                   settings.PACKAGE_NAME_FILEBROWSER).DIRECTORY
                except ImportError:
                    dir_name = "galleries"
                file_path = os.path.join(dir_name, self.slug, name)
                file_path = default_storage.save(file_path, ContentFile(data))
                self.images.add(GalleryImage(file=file_path))
            self.zip_import.delete(save=True)


class GalleryImage(Orderable):

    gallery = models.ForeignKey("Gallery", related_name="images")
    file = FileField(max_length=200, upload_to="galleries")
    description = models.CharField(max_length=1000, blank=True)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        """
        If no description is given when created, create one from the
        file name.
        """
        if not self.id and not self.description:
            name = self.file.path.split("/")[-1].rsplit(".", 1)[0]
            name = re.sub("[^a-zA-Z0-9]", " ", name.replace("'", ""))
            self.description = name.title()
        super(GalleryImage, self).save(*args, **kwargs)
