==========
Deployment
==========

Deployment of a Mezzanine site to production is mostly identical to 
deploying a regular Django site. Some considerations sholuld be made 
around the following aliases that need to be configured with your 
web server for hosting static files.

  * Your project's media files as per normal Django sites, defined by ``MEDIA_URL`` and ``MEDIA_ROOT``.
  * Grappelli's media files, defined by ``ADMIN_MEDIA_PREFIX`` and ``GRAPPELLI_MEDIA_PATH``.
  * Mezzanine's media files, defined by ``CONTENT_MEDIA_URL`` and ``CONTENT_MEDIA_PATH``.

For convenience, the management command ``media_paths`` is provided 
which will print out the actual values of each of these aliases and 
the paths they map to::

    $ python manage.py media_paths

Multi-Site
==========

Mezzanine currently supports multiple-site functionality through the use of the
Django `Sites` application, which comes bundled with Django (django.contrib.sites).
This functionality is actually always "turned on" in Mezzanine: a "single site"
deployment is a deployment of Mezzanine that references a single `site` record,
which is how Mezzanine is configured out of the box.  Migrating from a "single site" 
deployment to a "multiple site" deployment is as simple as adding another site to the 
Sites application's `site` table, and then creating a new runtime instance of Django 
that references that record via the SITE_ID setting in settings.py.

So, a multi-site mezzanine deployment that supports three sites will be configured as so:
  * A shared database system will exist to store all of the data used by the system.
  * Three separate runtime instances of Django, each with its own settings.py file, will be created, each responsible for managing a single site
  * Each settings.py file used by these three instances will point to a different `site` record via the SITE_ID setting.
  * If the different sites use different themes or templates, then different theme directories or INSTALLED_APPS can be specified for each of these three independant instances.
  * All three settings.py files will reference the same database.

The content of each individual site will be editable via the admin application running
within the instance that embodies that site.  In other words, the admin running at
siteone.com/admin will allow the content of siteone.com to be edited, while the admin
running at `sitetwo.com/admin` will allow the content of sitetwo.com to be edited, and
only that content.

For more information regarding the Django sites application, see the Django docs:

http://docs.djangoproject.com/en/1.3/ref/contrib/sites/

Twitter Feeds
=============

If Twitter feeds are implemented in your templates, a cron job is 
required that will run the following management command:: 

    $ python manage.py poll_twitter
    
This ensures that the data is always available in the site's database 
when accessed, and allows you to control how often the Twitter API is 
queried.
