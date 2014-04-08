from __future__ import unicode_literals
from future.builtins import str
from future.utils import native

import os
from shutil import rmtree
from uuid import uuid4

from mezzanine.conf import settings
from mezzanine.core.templatetags.mezzanine_tags import thumbnail
from mezzanine.galleries.models import Gallery, GALLERIES_UPLOAD_DIR
from mezzanine.utils.tests import TestCase, copy_test_to_media


class GalleriesTests(TestCase):

    def test_gallery_import(self):
        """
        Test that a gallery creates images when given a zip file to
        import, and that descriptions are created.
        """
        zip_name = "gallery.zip"
        copy_test_to_media("mezzanine.core", zip_name)
        title = native(str(uuid4()))  # i.e. Py3 str / Py2 unicode
        gallery = Gallery.objects.create(title=title, zip_import=zip_name)
        images = list(gallery.images.all())
        self.assertTrue(images)
        self.assertTrue(all([image.description for image in images]))
        # Clean up.
        rmtree(os.path.join(settings.MEDIA_ROOT,
                            GALLERIES_UPLOAD_DIR, title))

    def test_thumbnail_generation(self):
        """
        Test that a thumbnail is created and resized.
        """
        try:
            from PIL import Image
        except ImportError:
            return
        image_name = "image.jpg"
        size = (24, 24)
        copy_test_to_media("mezzanine.core", image_name)
        thumb_name = os.path.join(settings.THUMBNAILS_DIR_NAME, image_name,
                                  image_name.replace(".", "-%sx%s." % size))
        thumb_path = os.path.join(settings.MEDIA_ROOT, thumb_name)
        thumb_image = thumbnail(image_name, *size)
        self.assertEqual(os.path.normpath(thumb_image.lstrip("/")), thumb_name)
        self.assertNotEqual(os.path.getsize(thumb_path), 0)
        thumb = Image.open(thumb_path)
        self.assertEqual(thumb.size, size)
        # Clean up.
        del thumb
        os.remove(os.path.join(settings.MEDIA_ROOT, image_name))
        os.remove(os.path.join(thumb_path))
        rmtree(os.path.join(os.path.dirname(thumb_path)))
