from __future__ import unicode_literals
from future.builtins import str
from future.utils import native

from io import BytesIO
import os
from string import punctuation
from zipfile import ZipFile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
try:
    from django.utils.encoding import force_text
except ImportError:
    # Django < 1.5
    from django.utils.encoding import force_unicode as force_text
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Orderable, RichText
from mezzanine.pages.models import Page
from mezzanine.utils.importing import import_dotted_path
from mezzanine.utils.models import upload_to


# Set the directory where gallery images are uploaded to,
# either MEDIA_ROOT + 'galleries', or filebrowser's upload
# directory if being used.
GALLERIES_UPLOAD_DIR = "galleries"
if settings.PACKAGE_NAME_FILEBROWSER in settings.INSTALLED_APPS:
    fb_settings = "%s.settings" % settings.PACKAGE_NAME_FILEBROWSER
    try:
        GALLERIES_UPLOAD_DIR = import_dotted_path(fb_settings).DIRECTORY
    except ImportError:
        pass


class Gallery(Page, RichText):
    """
    Page bucket for gallery photos.
    """

    zip_import = models.FileField(verbose_name=_("Zip import"), blank=True,
        upload_to=upload_to("galleries.Gallery.zip_import", "galleries"),
        help_text=_("Upload a zip file containing images, and "
                    "they'll be imported into this gallery."))

    class Meta:
        verbose_name = _("Gallery")
        verbose_name_plural = _("Galleries")

    def save(self, delete_zip_import=True, *args, **kwargs):
        """
        If a zip file is uploaded, extract any images from it and add
        them to the gallery, before removing the zip file.
        """
        super(Gallery, self).save(*args, **kwargs)
        if self.zip_import:
            zip_file = ZipFile(self.zip_import)
            for name in zip_file.namelist():
                data = zip_file.read(name)
                try:
                    from PIL import Image
                    image = Image.open(BytesIO(data))
                    image.load()
                    image = Image.open(BytesIO(data))
                    image.verify()
                except ImportError:
                    pass
                except:
                    continue
                name = os.path.split(name)[1]
                # This is a way of getting around the broken nature of
                # os.path.join on Python 2.x. See also the comment below.
                if isinstance(name, bytes):
                    tempname = name.decode('utf-8')
                else:
                    tempname = name

                # A gallery with a slug of "/" tries to extract files
                # to / on disk; see os.path.join docs.
                slug = self.slug if self.slug != "/" else ""
                path = os.path.join(GALLERIES_UPLOAD_DIR, slug, tempname)
                try:
                    saved_path = default_storage.save(path, ContentFile(data))
                except UnicodeEncodeError:
                    from warnings import warn
                    warn("A file was saved that contains unicode "
                         "characters in its path, but somehow the current "
                         "locale does not support utf-8. You may need to set "
                         "'LC_ALL' to a correct value, eg: 'en_US.UTF-8'.")
                    # The native() call is needed here around str because
                    # os.path.join() in Python 2.x (in posixpath.py)
                    # mixes byte-strings with unicode strings without
                    # explicit conversion, which raises a TypeError as it
                    # would on Python 3.
                    path = os.path.join(GALLERIES_UPLOAD_DIR, slug,
                                        native(str(name, errors="ignore")))
                    saved_path = default_storage.save(path, ContentFile(data))
                self.images.add(GalleryImage(file=saved_path))
            if delete_zip_import:
                zip_file.close()
                self.zip_import.delete(save=True)


@python_2_unicode_compatible
class GalleryImage(Orderable):

    gallery = models.ForeignKey("Gallery", related_name="images")
    file = FileField(_("File"), max_length=200, format="Image",
        upload_to=upload_to("galleries.GalleryImage.file", "galleries"))
    description = models.CharField(_("Description"), max_length=1000,
                                                           blank=True)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        """
        If no description is given when created, create one from the
        file name.
        """
        if not self.id and not self.description:
            name = force_text(self.file.name)
            name = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            name = name.replace("'", "")
            name = "".join([c if c not in punctuation else " " for c in name])
            # str.title() doesn't deal with unicode very well.
            # http://bugs.python.org/issue6412
            name = "".join([s.upper() if i == 0 or name[i - 1] == " " else s
                            for i, s in enumerate(name)])
            self.description = name
        super(GalleryImage, self).save(*args, **kwargs)
