=============
Configuration
=============

Mezzanine provides a centralised system for defining settings within 
your project and applications that can then be edited by admin users. 
The package ``mezzanine.settings`` contains the models for storing 
editable settings in the database as well as the functions for 
registering and loading these settings throughout your project.

Registering Settings
====================

Settings are defined by creating a module named ``defaults.py`` inside 
one or more of the applications defined in your project's 
``settings.INSTALLED_APPS`` setting. Inside your ``defaults.py`` module 
you then call the function ``mezzanine.settings.register_setting`` for 
each setting you want to define which takes four keyword arguments:

  * ``name``: The name of the setting.
  * ``description``: The description of the setting.
  * ``editable``: If ``True``, the setting will be editable via the admin.
  * ``default``: The default value of the setting. 

For example suppose we had a ``gallery`` application and we wanted to 
create a setting that controls the number of photos displayed per page, 
we would define the following in ``gallery.defaults``::

    from mezzanine.settings import register_setting

    register_setting(
        name="GALLERY_PHOTOS_PER_PAGE",
        description="The number of gallery photos to show on a single page.",
        editable=True,
        default=10,
    )

Reading Settings
================

Accessing the values of settings defined using the above approach is similar 
to importing settings from ``django.conf``. The function 
``mezzanine.settings.load_settings`` takes a variable number of arguments, 
each containing the name of a setting to load. The return value is an 
object containing each of the requested setting names as attributes. 
Values for *all* of the settings in the returned object are loaded when 
one of the attributes are first accessed. Continuing on from our previous 
example, suppose we have a view for photos::

    from django.shortcuts import render_to_response
    from mezzanine.settings import load_settings
    from models import GalleryImage
    
    def gallery_view(request):
        settings = load_settings("GALLERY_PHOTOS_PER_PAGE", "ANOTHER_SETTING")
        photos_per_page = settings.GALLERY_PHOTOS_PER_PAGE
        photos = GalleryImage.objects.all()[:photos_per_page]
        return render_to_respone("gallery/gallery.html", {"photos": photos, RequestContext(request)})

When defining editable settings, care should be taken when considering 
where in your project the setting will be used. For example if a setting 
is used in a ``urlpattern`` or the creation of a ``model`` class it would 
only be read when your site is first loaded, and therefore having it 
change at a later point by an admin user would not have any effect without 
reloading your entire project. In the snippet above by loading the 
settings object within the view the value of the setting is loaded each 
time the view is run. This ensures that if the value of the setting has 
been changed by an admin user it will be reflected on the website.

Default Settings
================

Mezzanine defines the following settings:

.. include:: settings.rst
