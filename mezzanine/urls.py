
from django.conf import settings
from django.conf.urls.defaults import *

from mezzanine.conf import load_settings


mezz_settings = load_settings("BLOG_SLUG")


urlpatterns = patterns("",
    ("^", include("mezzanine.core.urls")),
)

if "mezzanine.blog" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^%s/" % mezz_settings.BLOG_SLUG, include("mezzanine.blog.urls")),
    )
if "mezzanine.pages" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^", include("mezzanine.pages.urls")),
    )
