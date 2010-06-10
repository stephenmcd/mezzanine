
import os.path

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# Unregister these models installed by default (occurs in urlconf).
ADMIN_REMOVAL = ()

# Blog feed settings.
BLOG_TITLE = "The Mezzanine Blog"
BLOG_DESCRIPTION = "The Mezzanine Blog"
# Credentials for bit.ly URL shortening service.
BLOG_BITLY_USER = None
BLOG_BITLY_KEY = None

# Number of blog posts to show on a blog listing page.
BLOG_POST_PER_PAGE = 5

# Maximum number of paging links to show on a blog listing page.
BLOG_POST_MAX_PAGING_LINKS = 10

# Shortname when using the Disqus comments system (http://disqus.com).
COMMENTS_DISQUS_SHORTNAME = None

# Disqus user's API key for displaying recent comments in the admin dashboard.
COMMENTS_DISQUS_KEY = None

# If True, the built-in comments are approved by default.
COMMENTS_DEFAULT_APPROVED = True

# Number of latest comments to show in the admin dashboard.
COMMENTS_NUM_LATEST = 5

# If True, unapproved comments will have a placeholder visible on the site 
# with a "waiting for approval" or "comment removed" message based on the 
# workflow around the COMMENTS_DEFAULT_APPROVED setting - if True then the 
# former message is used, if False then the latter.
COMMENTS_UNAPPROVED_VISIBLE = True

# Media files for admin.
CONTENT_MEDIA_PATH = os.path.join(os.path.dirname(__file__), "core", "media")
CONTENT_MEDIA_URL = "/content_media/"

# Content status choices.
CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, _("Draft")),
    (CONTENT_STATUS_PUBLISHED, _("Published")),
)

# Number of different sizes given to tags when shown as a cloud.
TAG_CLOUD_SIZES = 4

