
from django.conf.urls.defaults import patterns, url
from django.conf import settings


# Page patterns.
urlpatterns = patterns("mezzanine.pages.views",
    url("^admin_page_ordering/$", "admin_page_ordering",
        name="admin_page_ordering"),
    url("^(?P<slug>.*)%s$" % ("/" if settings.APPEND_SLASH else ""),
        "page", name="page"),
)
