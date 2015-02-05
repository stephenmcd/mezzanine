# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'Query.value'
        db.alter_column('twitter_query', 'value', self.gf('django.db.models.fields.CharField')(max_length=140))
    
    
    def backwards(self, orm):
        
        # Changing field 'Query.value'
        db.alter_column('twitter_query', 'value', self.gf('django.db.models.fields.CharField')(max_length=50))
    
    
    models = {
        'twitter.query': {
            'Meta': {'object_name': 'Query'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interested': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'twitter.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'query': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tweets'", 'to': "orm['twitter.Query']"}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'retweeter_full_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'retweeter_profile_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'retweeter_user_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }
    
    complete_apps = ['twitter']
