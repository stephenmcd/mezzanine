# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Query'
        db.create_table('twitter_query', (
            ('interested', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('twitter', ['Query'])

        # Adding model 'Tweet'
        db.create_table('twitter_tweet', (
            ('retweeter_profile_image_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('remote_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('retweeter_user_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('profile_image_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('query', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tweets', to=orm['twitter.Query'])),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('retweeter_full_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal('twitter', ['Tweet'])


    def backwards(self, orm):

        # Deleting model 'Query'
        db.delete_table('twitter_query')

        # Deleting model 'Tweet'
        db.delete_table('twitter_tweet')


    models = {
        'twitter.query': {
            'Meta': {'object_name': 'Query'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interested': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
