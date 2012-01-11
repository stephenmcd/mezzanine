
from optparse import make_option
from urlparse import urlparse

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags

from mezzanine.utils.html import decode_entities


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
        content=None, comments=None, old_url=None, categories=None):
        """
        Adds a post to the post list for processing.

        Attributes:
            pub_date is assumed to be a datetime object.
        """
        if not title:
            title = decode_entities(strip_tags(content).split(". ")[0])
        if categories is None:
            categories = []
        if tags is None:
            tags = []
        if comments is None:
            comments = []
        self.posts.append({
            "title": title,
            "publish_date": pub_date,
            "content": content,
            "categories": categories,
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
            "user_name": name,
            "user_email": email,
            "submit_date": pub_date,
            "user_url": website,
            "comment": body,
        })

    def handle(self, *args, **options):
        """
        Processes the converted data into the Mezzanine database correctly.

        Attributes:
            mezzanine_user: the user to put this data in against
            date_format: the format the dates are in for posts and comments
        """

        from mezzanine.blog.models import BlogPost, BlogCategory
        from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
        from mezzanine.generic.models import AssignedKeyword, Keyword
        from mezzanine.generic.models import ThreadedComment

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
            categories = post.pop("categories")
            tags = post.pop("tags")
            comments = post.pop("comments")
            old_url = post.pop("old_url")
            post_args = post
            post_args["user"] = mezzanine_user
            post_args["status"] = CONTENT_STATUS_PUBLISHED
            post, created = BlogPost.objects.get_or_create(**post_args)

            for tag in tags:
                keyword, created = Keyword.objects.get_or_create(title=tag)
                post.keywords.add(AssignedKeyword(keyword=keyword))

            for name in categories:
                cat, created = BlogCategory.objects.get_or_create(title=name)
                print "Importing Category by: %s" % cat
                post.categories.add(cat)

            for comment in comments:
                if verbosity >= 1:
                    print "Importing comment by: %s" % comment["user_name"]
                comment["site"] = site
                post.comments.add(ThreadedComment(**comment))

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
