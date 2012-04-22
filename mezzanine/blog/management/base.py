
from optparse import make_option
from urlparse import urlparse

from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags

from mezzanine.pages.models import RichTextPage
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
        make_option('--nav', action='store_true', dest='in_navigation',
            help='Add pages to navigation'),
        make_option('--foot', action='store_true', dest='in_footer',
            help='Add pages to footer navigation'),
    )

    def __init__(self, **kwargs):
        self.posts = []
        self.pages = []
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

    def add_page(self, title=None, pub_date=None, tags=None,
         content=None, old_url=None, old_id=None, old_parent_id=None):
        if not title:
            title = decode_entities(strip_tags(content).split(". ")[0])
        if tags is None:
            tags = []
        self.pages.append({
            "title": title.replace('\n', ' ')[:RichTextPage._meta.get_field('title').max_length - 1],
            "publish_date": pub_date,
            "content": content,
            "tags": tags,
            "old_url": old_url,
            "old_id" : old_id,
            "old_parent_id" : old_parent_id,
        })
        return self.pages[-1]

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

    def trunc_for_model_field(self, string, model, field, user_input=False):
        '''
        Truncates a string for a model, in the format.
        optional user_input = string to display to user to decide to truncate
        '''
        try:
            if model._meta.get_field(field).max_length and len(string) > model._meta.get_field(field).max_length:
#                print len(string)
#                print model._meta.get_field(field).max_length
#                print field
                if user_input:
                    continue_words = set(['y', 'yes'])
                    change_words = set(['c', 'change'])
                    new_str = string[:model._meta.get_field(field).max_length-1]
                    do_trunc = raw_input('Would you like to truncate the : %s for model %s:\n to: %s (y[es]/n[o]/c[hange]):  ' % (user_input, str(model), new_str))
                    if not continue_words.intersection(do_trunc.lower()):
                        if change_words.intersection(do_trunc.lower()):
                            return raw_input('Enter new title - max length = %s:  ' % model._meta.get_field(field).max_length)
                        else:
                            return False
                string = new_str
        except TypeError:
            pass
        return string

    def trunc_for_model(self, obj, model, **kwargs):
        '''
        Truncates a string or dict values for a model, in the format:
          'var' : 'value'
        Where var is both a dict value, and model field.
        optional kwargs:
          user_input = 'title to display for user option'
          field = single dict field to truncate
        '''
        field = kwargs.get('field', False)
        if type(obj) == str:
            if not field:
                raise Exception('truncating string for model requires kwarg field to be set')
            return self.trunc_for_model_field(obj, model, **kwargs)
        elif type(obj) == dict:
            if kwargs.get('field', False):
                obj[field] = self.trunc_for_model_field(obj[field], model, field, **kwargs)
            else:
                for var, val in obj.iteritems():
                    obj[var] = self.trunc_for_model_field(val, model, var, **kwargs)
            return obj

    def handle(self, *args, **options):
        """
        Processes the converted data into the Mezzanine database correctly.

        Attributes:
            mezzanine_user: the user to put this data in against
            date_format: the format the dates are in for posts and comments
        """

        from mezzanine.blog.models import BlogPost, BlogCategory
        from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
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
            post_args = self.trunc_for_model(post, BlogPost, user_input=post['title'])
            post_args["user"] = mezzanine_user
            post_args["status"] = CONTENT_STATUS_PUBLISHED
            post, created = BlogPost.objects.get_or_create(**post_args)

            for name in categories:
                name = self.trunc_for_model(name,
                                BlogCategory, field='title', user_input=name)
                if name and len(name) > 0:
                    cat, created = BlogCategory.objects.get_or_create(title=name)
                    print "Importing Category by: %s" % cat
                    post.categories.add(cat)

            for comment in comments:
                if verbosity >= 1:
                    print "Importing comment by: %s" % comment["user_name"]

                comment = self.trunc_for_model(comment,
                    ThreadedComment, user_input='Comment from %s' % comment["user_name"])
                comment["site"] = site
                post.comments.add(ThreadedComment(**comment))
            self.add_meta(post, tags, old_url)

        in_footer = options.get('in_footer', False)
        if not in_footer:
            in_footer = False
        in_navigation = options.get('in_navigation', False)
        if not in_navigation:
            in_navigation = False
        parents = []
#        print 'in_footer = %s' % in_footer
#        print 'in_navigation = %s' % in_navigation
        for page in self.pages:
            if verbosity >= 1:
                print "Importing page titled: %s" % page["title"]
            tags = page.pop("tags")
            old_url = page.pop("old_url")
            old_id = page.pop("old_id")
            old_parent_id = page.pop("old_parent_id")
            page_args = page
            page_args["status"] = CONTENT_STATUS_PUBLISHED
            page_args['in_navigation'] = in_navigation
            page_args['in_footer'] = in_footer
            page, created = RichTextPage.objects.get_or_create(**page_args)
            self.add_meta(page, tags, old_url)

            parents.append({
                'old_id' : old_id,
                'old_parent_id' : old_parent_id,
                'page' : page,
            })

        for obj in parents:
#            print '%s : %s : %s : %s' % (obj['old_id'], obj['old_parent_id'], obj['page'].id, obj['page'].title)
            if obj['old_parent_id']:
                for parent in parents:
                    if parent['old_id'] == obj['old_parent_id']:
                        obj['page'].parent = parent['page']
                        obj['page'].save()
                        continue

    def add_meta(self, post, tags, old_url=None):
        from mezzanine.generic.models import AssignedKeyword, Keyword

        for tag in tags:
            keyword, created = Keyword.objects.get_or_create(title=tag)
            post.keywords.add(AssignedKeyword(keyword=keyword))

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
