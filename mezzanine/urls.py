
from django.conf.urls.defaults import *

from mezzanine.conf import settings


urlpatterns = patterns("",
    ("^", include("mezzanine.core.urls")),
)

if "mezzanine.blog" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^%s/" % settings.BLOG_SLUG, include("mezzanine.blog.urls")),
    )
if "mezzanine.pages" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^", include("mezzanine.pages.urls")),
    )
