
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from mezzanine.core.views import direct_to_template


admin.autodiscover()

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.
urlpatterns = patterns("",
    ("^admin/", include(admin.site.urls)),

    # Next pattern is the home view - defaults to the template
    # index.html, but if you'd like the homepage to be your blog,
    # remove the pattern below, and use the one commented out underneath
    # it. You'll also need to set BLOG_SLUG = "" in your settings.py
    # module, and delete the blog page object if it was installed,
    # to get this working
    url("^$", direct_to_template, {"template": "index.html"}, name="home"),
    # url("^$", "mezzanine.blog.views.blog_post_list", name="home"),

    # ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
    # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
    # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
    # WILL NEVER BE MATCHED!
    ("^", include("mezzanine.urls")),

)

# Adds ``STATIC_URL`` to the context.
handler500 = "mezzanine.core.views.server_error"
