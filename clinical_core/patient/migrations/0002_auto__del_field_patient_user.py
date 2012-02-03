# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Patient.user'
        db.delete_column('patient_patient', 'user_id')


    def backwards(self, orm):
        
        # Adding field 'Patient.user'
        db.add_column('patient_patient', 'user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)


    models = {
        'patient.patient': {
            'Meta': {'object_name': 'Patient'},
            'doc_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        }
    }

    complete_apps = ['patient']
