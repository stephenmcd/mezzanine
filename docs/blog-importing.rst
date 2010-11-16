==================================
Importing blogs from other systems
==================================

Mezzanine has the ability to import blog posts from other systems. Presently
there is support for WordPress and Blogger with experimental (partial) support
Tumblr and standard RSS feeds.

Importing a blog from another platform is done using the mezzanine import_blog 
management command using the following general style:

    $ python manage.py import_blog --blogtype=type --mezzanine_user=name [options]

For information about all the parameters that the command can take run the 
following in your project directory:

    $ python manage.py import_blog --help
    
Notes and known issues
======================

The system has been designed in this iteration to simply use one management
command. This may be split into individual commands at a later stage. This means
there are lots of parameters for import_blog. If you get the help message it has
specific examples for the different types of importation.

There is a known issue around to do with some formatting losses - specifically
the instance where a heading of some sort is followed by a paragraph tag or
another block HTML element that is not typically enclosed with a <P> tag is
followed by a paragraph. This is depends heavily on the originating platform
as to how it encodes the blog body copy. The import processor gets about 90% 
correct but you may need to do some quick clean up afterwards.

Generally speaking you shouldn't be able to import your data twice. There is a
check in place to do a create or update on both comments and posts as they are
processed so even if you do it a couple of times you should only end up with
the same amount of both. However if you have changed any data this will be
overwritten.

========================
Importing from Wordpress
========================

It is faster to import directly from your filesystem if you can (especially if 
you have a large blog with lots of comments).

Dependencies and pre-requisites
===============================

You will need to install Mark Pilgrim's feedparser library. This can be done
as simply as:

    $ easy_install feedparser
    
Similarly you can get the source and just drop it on your path somewhere.

Once complete you will need to export your Wordpress data ready for import. When
you have exported this you can either save it down to your local filesystem
(preferred option as it will be a lot quicker) or place it on a public server
in order to process (often the case if you are working on two live servers).

To export your Wordpress data, login to your Wordpress instance and go to
Settings -> Export

Select your filters if you want, but specifically posts will only be processed
(no pages as yet) and set to published only.

Once you have your export file have your path or URL to the export file handy.

Import process
==============

Once you have your export file import is as simple as running:

$ python manage.py import_blog --blogtype=wordpress --url=[path|url] --mezzanine-user=..

The url parameter can also be a file system path but it must go from the system
root and the mezzanine-user parameter is the user you wish to import under.

The process will run, indicating how far through it you are.

======================
Importing from Blogger
======================

The Blogger import currently has one known limitation which is there is a
maximum of 500 blogs or 500 comments per blog that can be imported. If you have
more than this it will truncate the feed. The import will still run however.

Dependencies and pre-requisites
===============================

The blogger import utilises the Google Data library extensively. This must be
installed before importing. To do this simply:

    $ easy_install gdata
    
If you don't want it in your packages just ensure it is on your path. You can
get the source from: http://code.google.com/p/gdata-python-client/

To import your blogger blog you need to enable one thing on your account and
to get one piece of data as follows:

    * log into your blogger account that you wish to import
    * click on settings - now look in the url and you'll see a url that ends in
        BlogID= and a big long number. That long number is your unique blog
        identifier. Copy it and save it for later.
    * While you're in settings go to "Site Feed" then set Allow Blog Feeds to
    be "Full" - this will give you everything in your Atom feed.
    
Now you're ready to import.

Import process
==============

To import you simply run the following command:

$ python manage.py import_blog --blogtype=blogger --blogger=blogid --mezzanine-user=..

The blogger parameter is the blogger ID you saved earlier and then you specify 
the mezzanine user you'd like to import all the data under.

This will then run and take a while to process as it's talking live to blogger
the whole time. Be patient, especially if you have a lot of comments to your
posts. There's an indicator to show how far through you are.

