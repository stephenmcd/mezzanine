===================
Twitter Integration
===================

.. deprecated:: 5.0
   :mod:`mezzanine.twitter` has been deprecated and will be removed in a
   future version.

The :mod:`mezzanine.twitter` application exposes the ability to consume,
store, and display your own tweets on your site in an efficient manner,
as well as the ability to send tweets when publishing new content to
the site.


Twitter Feeds
=============

If Twitter feeds are implemented in your templates, a cron job is
required that will run the following management command. For example,
if we want the tweets to be updated every 10 minutes::

    */10 * * * * python path/to/your/site/manage.py poll_twitter

This ensures that the data is always available in the site's database
when accessed, and allows you to control how often the Twitter API is
queried. Note that the Fabric script described earlier includes
features for deploying templates for cron jobs, which includes the
job for polling Twitter by default.

As of June 2013, Twitter also requires that all API access is
authenticated. For this you'll need to configure a Twitter application
with OAuth credentials for your site to access the Twitter API. These
credentials are configurable as Mezzanine settings. See the
:doc:`configuration` section for more information on these, as well as
the `Twitter developer site <https://dev.twitter.com/>`_ for info on
creating an application and configuring your OAuth credentials.


Sending Tweets
==============

When setting up a Twitter application, you'll also be able to configure
the permissions your OAuth credentials have against the Twitter API. To
consume Twitter feeds, only read permissions are needed, but you may
also choose to allow both read and write permissions. With write
permissions enabled, you'll then also be able to expose the option in
Mezzanine's admin interface for automatically tweeting new blog posts
(or your own custom content) when they're published.

To enable this, simply install the `python-twitter
<https://pypi.python.org/pypi/python-twitter>` library. With the library
installed and credential setttings set, blog posts in the admin will
have a "Send to Twitter" checkbox, which when checked, will send a tweet
with the post's title and URL.

You can also add this functionality to your own admin classes by making
use of :class:`mezzanine.twitter.admin.TweetableAdminMixin`. See
:class:`mezzanine.blog.admin.BlogPostAdmin` for an example.
