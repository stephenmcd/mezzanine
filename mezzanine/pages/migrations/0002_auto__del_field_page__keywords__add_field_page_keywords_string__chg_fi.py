# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Page._keywords'
        db.delete_column('pages_page', '_keywords')

        # Adding field 'Page.keywords_string'
        db.add_column('pages_page', 'keywords_string', self.gf('django.db.models.fields.CharField')(default='', max_length=500, blank=True), keep_default=False)

        # Removing M2M table for field keywords on 'Page'
        db.delete_table('pages_page_keywords')

        # Changing field 'Page.description'
        db.alter_column('pages_page', 'description', self.gf('django.db.models.fields.TextField')(blank=True))
    
    
    def backwards(self, orm):
        
        # Adding field 'Page._keywords'
        db.add_column('pages_page', '_keywords', self.gf('django.db.models.fields.CharField')(default='', max_length=500), keep_default=False)

        # Deleting field 'Page.keywords_string'
        db.delete_column('pages_page', 'keywords_string')

        # Adding M2M table for field keywords on 'Page'
        db.create_table('pages_page_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm['pages.page'], null=False)),
            ('keyword', models.ForeignKey(orm['core.keyword'], null=False))
        ))
        db.create_unique('pages_page_keywords', ['page_id', 'keyword_id'])

        # Changing field 'Page.description'
        db.alter_column('pages_page', 'description', self.gf('mezzanine.core.fields.HtmlField')(blank=True))
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
            'object_pk': ('django.db.models.fields.TextField', [], {})
        },
        'generic.keyword': {
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
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_model': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_footer': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'keywords': ('mezzanine.generic.fields.KeywordsField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.AssignedKeyword']"}),
            'keywords_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
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
