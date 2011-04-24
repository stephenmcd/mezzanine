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

Twitter Feeds
=============

If Twitter feeds are implemented in your templates, a cron job is
required that will run the following management command::

    $ python manage.py poll_twitter

This ensures that the data is always available in the site's database
when accessed, and allows you to control how often the Twitter API is
queried.
