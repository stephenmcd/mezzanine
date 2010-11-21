========================
Importing External Blogs
========================

Mezzanine has the ability to import blog posts from other blogging platforms. 
There is currently support for `WordPress <http://wordpress.org>`_ and 
`Blogger <http://blogger.com>`_, with partial support for 
`Tumblr <http://tumblr.com>`_ and standard RSS feeds.

Importing a blog from another platform is performed via a 
`Django management command <http://docs.djangoproject.com/en/dev/howto/custom-management-commands/>`_ 
with each supported platform having its own command.

  * Wordpress: ``import_wordpress``
  * Blogger: ``import_blogger``
  * Tumblr: ``import_tumblr``

Each command takes a Mezzanine username to assign the blog posts to as well
as certain arguments specific to the blog platform. For example to import an 
existing Wordpress blog::

    $ python manage.py import_wordpress --mezzanine-user=username [options]

Use the ``--help`` argument to learn more about the arguments specific to 
each blog platform's command. For example you can see all options for 
Wordpress by running::

    $ python manage.py import_wordpress --help
  
Known Issues
============

There are some known issues with HTML formatting loss - specifically where 
a heading tag is followed by a paragraph tag or another block HTML element 
that is not typically enclosed with a ``<P>`` tag is followed by a paragraph. 
This depends heavily on the originating platform and how it encodes the blog 
post's copy. The import processor gets this about 90% correct but you may 
need to do some quick clean up afterwards.

Generally speaking you shouldn't be able to import your data twice. There 
is a check in place to either create or update for both comments and posts as 
they are processed, so even if you run the importer multiple times you should 
only end up with data imported once. However if you have changed any data 
this will be overwritten.

Importing from Wordpress
========================

Dependencies
------------

  * Mark Pilgrim's `feedparser <http://www.feedparser.org/>`_ 
  
Import Process
--------------

The first step is to export your Wordpress data. Login to Wordpress and go 
to ``Settings -> Export``. Here you can select your filters, otherwise only 
published posts will be exported. Once you have saved your export file make 
a note of the location you saved it to.

.. note:: 

    It is faster to import directly from your filesystem if you can, 
    especially if you have a large blog with lots of comments.

The next step is to run the ``import_wordpress`` command where the 
``url`` argument contains the path or URL to your export file::

    $ python manage.py import_wordpress --mezzanine-user=.. --url=[path|URL] 

Importing from Blogger
======================

The Blogger import currently has one known limitation which is a
maximum of 500 blogs or 500 comments per blog that can be imported. If 
you have more than this the import will still but end up being truncated.

Dependencies
------------

 * Google's `gdata <http://code.google.com/p/gdata-python-client/>`_ Library

Import process
--------------

The first step is to obtain your Blogger ID. Login to Blogger and go to 
``Settings``. You'll see that the address in your browser end with 
``BlogID=XXX`` where ``XXX`` is your Blogger ID. Make a note of this and 
while you're in settings, go to ``Site Feed`` then set ``Allow Blog Feeds`` 
to be ``Full`` - this will give you all your data when you run the import.

The next step is to run the ``import_blogger`` command where the 
``blog_id`` argument contains the Blogger ID you retrieved::

    $ python manage.py import_blogger --mezzanine-user=.. --blog_id=blog_id

Importer API - Adding New Importers
===================================

The importer system has been designed to be extensible so that import 
commands can easily be added for other blogging platforms.

Each import command is a Django management command located in the 
``mezzanine.blog.management.commands`` package and should have its module 
named ``import_blogtype`` where ``blog_type`` is the name of the blogging 
platform the command is for. This module will then contain a class named 
``Command`` which subclasses ``mezzanine.blog.base.BaseImporterCommand``. 

The first step is to define any custom arguments the command will require 
using Python's `optparse <http://docs.python.org/library/optparse.html>`_ 
handling. These arguments will then be available as attributes of the 
``Command`` class when it is executed.

The main responsbility of the ``Command`` class is then to implement a 
``convert`` method which handles retrieving blog posts and comments from 
the particular blogging platform. The ``add_post`` and ``add_comment`` 
methods should be called inside the ``convert`` method, adding posts and 
comments respectively. The ``add_post`` method returns a post to be used 
with the ``add_comment`` method. For example::

    from optparse import make_option
    from django.core.management.base import CommandError
    from mezzanine.blog.manageurlment.base import BaseImporterCommand

    class Command(BaseImporterCommand):

        option_list = BaseImporterCommand.option_list + (
            make_option("-s", "--some_arg_name", dest="some_arg_var",
                help="Description of some_arg_name"),
        )

        def convert(self):
            # Perform the tasks that need to occur to retrieve blog posts.
            # We'll use an imaginary "posts" variable that contains a list of 
            # post dicts with keys: title, author, pub_date, tags and content. 
            # In this example we have access to the command line argument
            # "some_arg_name" via "self.some_arg_var"
            for retrieved_post in posts:
                added_post = self.add_post(**retrieved_post)
                # Another imaginary variable to demo the API.
                for retrieved_comment in comments:
                    self.add_comment(post=added_post, **retrieved_comment)

