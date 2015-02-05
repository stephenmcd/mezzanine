# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


SETTINGS_RENAMES = (
    ("SHOP_SSL_ENABLED", "SSL_ENABLED"),
    ("SHOP_SSL_FORCE_HOST", "SSL_FORCE_HOST"),
)


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for name_from, name_to in SETTINGS_RENAMES:
            try:
                setting = orm.Setting.objects.get(name=name_from)
            except orm.Setting.DoesNotExist:
                pass
            else:
                setting.name = name_to
                setting.save()


    def backwards(self, orm):
        "Write your backwards methods here."
        for name_to, name_from in SETTINGS_RENAMES:
            try:
                setting = orm.Setting.objects.get(name=name_from)
            except orm.Setting.DoesNotExist:
                pass
            else:
                setting.name = name_to
                setting.save()

    models = {
        'conf.setting': {
            'Meta': {'object_name': 'Setting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['conf']
