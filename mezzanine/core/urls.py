
from django.conf.urls.defaults import *


urlpatterns = patterns("mezzanine.core.views",
    url("^admin_keywords_submit/$", "admin_keywords_submit",
        name="admin_keywords_submit"),
    url("^edit/$", "edit", name="edit"),
    url("^search/$", "search", name="search"),
)
