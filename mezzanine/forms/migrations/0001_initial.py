# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = [
        ('pages', '0001_initial'),
        ]

    def forwards(self, orm):

        # Adding model 'Form'
        db.create_table('forms_form', (
            ('email_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('email_copies', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('button_text', self.gf('django.db.models.fields.CharField')(default=u'Submit', max_length=50)),
            ('response', self.gf('mezzanine.core.fields.HtmlField')()),
            ('content', self.gf('mezzanine.core.fields.HtmlField')()),
            ('send_email', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('email_subject', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('email_from', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal('forms', ['Form'])

        # Adding model 'Field'
        db.create_table('forms_field', (
            ('field_type', self.gf('django.db.models.fields.CharField')(max_length=55)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['forms.Form'])),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('choices', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('forms', ['Field'])

        # Adding model 'FormEntry'
        db.create_table('forms_formentry', (
            ('entry_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries', to=orm['forms.Form'])),
        ))
        db.send_create_signal('forms', ['FormEntry'])

        # Adding model 'FieldEntry'
        db.create_table('forms_fieldentry', (
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['forms.FormEntry'])),
            ('field_id', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal('forms', ['FieldEntry'])


    def backwards(self, orm):

        # Deleting model 'Form'
        db.delete_table('forms_form')

        # Deleting model 'Field'
        db.delete_table('forms_field')

        # Deleting model 'FormEntry'
        db.delete_table('forms_formentry')

        # Deleting model 'FieldEntry'
        db.delete_table('forms_fieldentry')


    models = {
        'core.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forms.field': {
            'Meta': {'object_name': 'Field'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '55'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['forms.Form']"}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'forms.fieldentry': {
            'Meta': {'object_name': 'FieldEntry'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['forms.FormEntry']"}),
            'field_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        'forms.form': {
            'Meta': {'object_name': 'Form', '_ormbases': ['pages.Page']},
            'button_text': ('django.db.models.fields.CharField', [], {'default': "u'Submit'", 'max_length': '50'}),
            'content': ('mezzanine.core.fields.HtmlField', [], {}),
            'email_copies': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'response': ('mezzanine.core.fields.HtmlField', [], {}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'forms.formentry': {
            'Meta': {'object_name': 'FormEntry'},
            'entry_time': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['forms.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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

    complete_apps = ['forms']
