# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = [
        ("core", "0001_initial"),
        ]

    def forwards(self, orm):

        # Adding model 'BlogPost'
        db.create_table('blog_blogpost', (
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blogposts', null=True, to=orm['blog.BlogCategory'])),
            ('description', self.gf('mezzanine.core.fields.HtmlField')(blank=True)),
            ('_keywords', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.HtmlField')()),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='blogposts', to=orm['auth.User'])),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('blog', ['BlogPost'])

        # Adding M2M table for field keywords on 'BlogPost'
        db.create_table('blog_blogpost_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('blogpost', models.ForeignKey(orm['blog.blogpost'], null=False)),
            ('keyword', models.ForeignKey(orm['core.keyword'], null=False))
        ))
        db.create_unique('blog_blogpost_keywords', ['blogpost_id', 'keyword_id'])

        # Adding model 'BlogCategory'
        db.create_table('blog_blogcategory', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('blog', ['BlogCategory'])

        # Adding model 'Comment'
        db.create_table('blog_comment', (
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('email_hash', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('by_author', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('blog_post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['blog.BlogPost'])),
            ('replied_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['blog.Comment'])),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('blog', ['Comment'])


    def backwards(self, orm):

        # Deleting model 'BlogPost'
        db.delete_table('blog_blogpost')

        # Removing M2M table for field keywords on 'BlogPost'
        db.delete_table('blog_blogpost_keywords')

        # Deleting model 'BlogCategory'
        db.delete_table('blog_blogcategory')

        # Deleting model 'Comment'
        db.delete_table('blog_comment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'blog.blogcategory': {
            'Meta': {'object_name': 'BlogCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'blog.blogpost': {
            'Meta': {'object_name': 'BlogPost'},
            '_keywords': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blogposts'", 'null': 'True', 'to': "orm['blog.BlogCategory']"}),
            'content': ('mezzanine.core.fields.HtmlField', [], {}),
            'description': ('mezzanine.core.fields.HtmlField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Keyword']", 'symmetrical': 'False', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blogposts'", 'to': "orm['auth.User']"})
        },
        'blog.comment': {
            'Meta': {'object_name': 'Comment'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'blog_post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['blog.BlogPost']"}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'by_author': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_hash': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'replied_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': "orm['blog.Comment']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['blog']
