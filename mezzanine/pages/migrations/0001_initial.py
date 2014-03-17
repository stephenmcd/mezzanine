# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = [
        ('core', '0001_initial'),
        ]

    def forwards(self, orm):

        # Adding model 'Page'
        db.create_table('pages_page', (
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['pages.Page'])),
            ('description', self.gf('mezzanine.core.fields.HtmlField')(blank=True)),
            ('_keywords', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('in_footer', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('short_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('login_required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('titles', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('content_model', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('in_navigation', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('pages', ['Page'])

        # Adding M2M table for field keywords on 'Page'
        db.create_table('pages_page_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm['pages.page'], null=False)),
            ('keyword', models.ForeignKey(orm['core.keyword'], null=False))
        ))
        db.create_unique('pages_page_keywords', ['page_id', 'keyword_id'])

        # Adding model 'ContentPage'
        db.create_table('pages_contentpage', (
            ('content', self.gf('mezzanine.core.fields.HtmlField')()),
            ('page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('pages', ['ContentPage'])

    def backwards(self, orm):

        # Deleting model 'Page'
        db.delete_table('pages_page')

        # Removing M2M table for field keywords on 'Page'
        db.delete_table('pages_page_keywords')

        # Deleting model 'ContentPage'
        db.delete_table('pages_contentpage')


    models = {
        'core.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pages.contentpage': {
            'Meta': {'object_name': 'ContentPage', '_ormbases': ['pages.Page']},
            'content': ('mezzanine.core.fields.HtmlField', [], {}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'})
        },
        'pages.page': {
            'Meta': {'object_name': 'Page'},
            '_keywords': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_model': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'description': ('mezzanine.core.fields.HtmlField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_footer': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Keyword']", 'symmetrical': 'False', 'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['pages.Page']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'titles': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        }
    }

    complete_apps = ['pages']
