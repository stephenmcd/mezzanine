
from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns("", 
    ("^", include("mezzanine.core.urls")),
)

if "mezzanine.blog" in settings.INSTALLED_APPS:
    urlpatterns += patterns("", 
        ("^blog/", include("mezzanine.blog.urls")),
    )
if "mezzanine.pages" in settings.INSTALLED_APPS:
    urlpatterns += patterns("", 
        ("^", include("mezzanine.pages.urls")),
    )

