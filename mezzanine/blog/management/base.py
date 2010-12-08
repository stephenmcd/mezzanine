
from optparse import make_option
from urlparse import urlparse

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from mezzanine.blog.models import BlogPost, Comment
from mezzanine.core.models import Keyword, CONTENT_STATUS_PUBLISHED


class BaseImporterCommand(BaseCommand):
    """
    Base importer command for blogging platform specific management
    commands to subclass when importing blog posts into Mezzanine.
    The ``handle_import`` method should be overridden to provide the
    import mechanism specific to the blogging platform being dealt with.
    """

    option_list = BaseCommand.option_list + (
        make_option("-m", "--mezzanine-user", dest="mezzanine_user",
            help="Mezzanine username to assign the imported blog posts to."),
    )

    def __init__(self, **kwargs):
        self.posts = []
        super(BaseImporterCommand, self).__init__(**kwargs)

    def add_post(self, title=None, pub_date=None, tags=None,
        content=None, comments=None, old_url=None):
        """
        Adds a post to the post list for processing.

        Attributes:
            pub_date is assumed to be a datetime object.
        """
        if tags is None:
            tags = []
        if comments is None:
            comments = []
        self.posts.append({
            "title": title,
            "publish_date": pub_date,
            "content": content,
            "tags": tags,
            "comments": comments,
            "old_url": old_url,
        })
        return self.posts[-1]

    def add_comment(self, post=None, name=None, email=None, pub_date=None,
        website=None, body=None):
        """
        Adds a comment to the post provided.

        Attributes:
            pub_date is assumed to be a date time object.
        """
        if post is None:
            if not self.posts:
                raise CommandError("Cannot add comments without posts")
            post = self.posts[-1]
        post["comments"].append({
            "name": name,
            "email": email,
            "time_created": pub_date,
            "website": website,
            "body": body,
        })

    def handle(self, *args, **options):
        """
        Processes the converted data into the Mezzanine database correctly.

        Attributes:
            mezzanine_user: the user to put this data in against
            date_format: the format the dates are in for posts and comments
        """

        mezzanine_user = options.get("mezzanine_user")
        site = Site.objects.get_current()
        verbosity = int(options.get("verbosity", 1))

        # Validate the Mezzanine user.
        if mezzanine_user is None:
            raise CommandError("No Mezzanine user has been specified")
        try:
            mezzanine_user = User.objects.get(username=mezzanine_user)
        except User.DoesNotExist:
            raise CommandError("Invalid Mezzanine user: %s" % mezzanine_user)

        # Run the subclassed ``handle_import`` and save posts, tags and
        # comments to the DB.
        self.handle_import(options)
        for post in self.posts:

            if verbosity >= 1:
                print "Importing post titled: %s" % post["title"]
            tags = post.pop("tags")
            comments = post.pop("comments")
            old_url = post.pop("old_url")

            post, created = BlogPost.objects.get_or_create(
                user=mezzanine_user, status=CONTENT_STATUS_PUBLISHED, **post)

            for tag in tags:
                keyword, created = Keyword.objects.get_or_create(title=tag)
                post.keywords.add(keyword)
            post.set_searchable_keywords()

            for comment in comments:
                if verbosity >= 1:
                    print "Importing comment by: %s" % comment["name"]
                comment["blog_post"] = post
                comment, created = Comment.objects.get_or_create(**comment)

            if old_url is not None:
                redirect, created = Redirect.objects.get_or_create(site=site,
                    old_path=urlparse(old_url).path)
                redirect.new_path = urlparse(post.get_absolute_url()).path
                redirect.save()

    def handle_import(self, options):
        """
        Should be overridden by subclasses - performs the conversion from
        the originating data source into the lists of posts and comments
        ready for processing.
        """
        raise NotImplementedError
