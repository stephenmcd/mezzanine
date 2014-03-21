# encoding: utf-8

import datetime
from south.db import db
from south.v2 import DataMigration
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor, \
                                            ManyRelatedObjectsDescriptor

try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)

class Migration(DataMigration):

    def forwards(self, orm):
        OrmCategory = orm['blog.blogcategory']
        blogcategories = OrmCategory._base_manager.all()

        # This block wll try to determine what additional many-to-many fields
        # may be pointing to the BlogCategory, unknown to mezzanine, by looking
        # at the live orm
        try:
            from mezzanine.blog.models import BlogCategory
            additional_fields = []
            for attr_name in dir(BlogCategory):
                attr = getattr(BlogCategory, attr_name)
                if isinstance(attr, ManyRelatedObjectsDescriptor) and \
                   attr.related.parent_model is BlogCategory and \
                   attr_name != "blogposts":
                    model = attr.related.model
                    field = attr.related.field.name
                    additional_fields.append((field, model, attr_name))
        except:
            additional_fields = []

        for category in blogcategories:
            posts = category.blogposts.all()
            site_dict = {}
            for post in posts:
                site = post.site
                dict_category = site_dict.get(site.pk, None)
                if not dict_category:
                    dict_category = OrmCategory(site=site, slug=category.slug, title=category.title)
                    dict_category.save()
                    site_dict[site.pk] = dict_category
                post.categories.remove(category)
                post.categories.add(dict_category)

            # This try block will attempt to find other objects that might be related
            # to the BlogCategory via a many-to-many relation outside of Mezzanine. It
            # will then attempt to disassociate that object from the old category
            # to be deleted, and then attach the new catetegory that will replace it.
            #
            # The risk here is that this is being run against a live model rather than
            # a frozen model.  Although that is a risk, if the live model is out of sync
            # it will generate errors early on and exit before the database is touched.
            # The database should only be touched if the db matches the live orm for the
            # relevant models.
            #
            # Also note that for new installations none of this will be executed because
            # `blogcategories` above will be empty and nothing in this for loop will execute.
            #
            # The reason all of this is necessary is that it is impossible to delete
            # the old categories without removing all database references, otherwise
            # database constraints will be triggered and data could be corrupted.
            try:
                from mezzanine.blog.models import BlogCategory
                live_category = BlogCategory._base_manager.get(pk=category.pk)
                # If the live orm is out of sync, this should exit at the above line

                for field, model, related_name in additional_fields:
                    try:
                        # use _base_manager here because only _base_manager will ignore current site
                        related_set = model._base_manager.filter(**{ field : live_category })

                        # if the live orm for the related object is out of sync, it will exit here.
                        for related in related_set.all():

                            # First, determine the relevant site object
                            site = None
                            for attr_name in dir(related.__class__):
                                attr = getattr(related.__class__, attr_name)
                                if isinstance(attr, ReverseSingleRelatedObjectDescriptor) and \
                                   attr.field.rel.to is Site:
                                    site = getattr(related, attr_name)
                                    if site:
                                        break
                            if not site:
                                site = category.site

                            # Then grab the new category object that will replace the old one
                            dict_category = site_dict.get(site.pk, None)
                            if not dict_category:
                                orm_site = orm['sites.site'].objects.get(pk=site.pk)
                                dict_category = OrmCategory(site=orm_site, slug=category.slug,
                                                            title=category.title)
                                dict_category.save()
                                site_dict[site.pk] = dict_category
                            new_category = BlogCategory._base_manager.get(pk=dict_category.pk)
                            # Again, if the live orm is out of sync, this should exit at the above line

                            # THIS is the "dangerous" part, where the live orm is used to alter the db
                            # This should not be reached if the live orm is out of sync with the db
                            getattr(new_category, related_name).add(related)
                            getattr(live_category, related_name).remove(related)

                            assert(related in model._base_manager.filter(**{field:new_category}))
                            assert(related not in model._base_manager.filter(**{field:live_category}))

                    except Exception as e:
                        import pdb; pdb.set_trace()
                        "It may be OK just to continue."

            except Exception as e:
                import pdb; pdb.set_trace()
                "It may be OK just to continue"

            try:
                category.delete()
            except Exception as e:
                import pdb; pdb.set_trace()


    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        user_model_label: {
            'Meta': {'object_name': User.__name__, 'db_table': "'%s'" % User._meta.db_table},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'blog.blogcategory': {
            'Meta': {'object_name': 'BlogCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'blog.blogpost': {
            'Meta': {'ordering': "('-publish_date',)", 'object_name': 'BlogPost'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'blogposts'", 'blank': 'True', 'to': "orm['blog.BlogCategory']"}),
            #'comments': ('mezzanine.generic.fields.CommentsField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.ThreadedComment']"}),
            'comments_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            #'keywords': ('mezzanine.generic.fields.KeywordsField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.AssignedKeyword']"}),
            'keywords_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            #'rating': ('mezzanine.generic.fields.RatingField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.Rating']"}),
            'rating_average': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rating_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blogposts'", 'to': "orm['%s']" % user_orm_label})
        },
        'comments.comment': {
            'Meta': {'ordering': "('submit_date',)", 'object_name': 'Comment', 'db_table': "'django_comments'"},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_comment'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comment_comments'", 'null': 'True', 'to': "orm['%s']" % user_orm_label}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'user_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'generic.assignedkeyword': {
            'Meta': {'object_name': 'AssignedKeyword'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['generic.Keyword']"}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {})
        },
        'generic.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'generic.rating': {
            'Meta': {'object_name': 'Rating'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'generic.threadedcomment': {
            'Meta': {'ordering': "('submit_date',)", 'object_name': 'ThreadedComment', '_ormbases': ['comments.Comment']},
            'by_author': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['comments.Comment']", 'unique': 'True', 'primary_key': 'True'}),
            'email_hash': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'replied_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'null': 'True', 'to': "orm['generic.ThreadedComment']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['blog']
