# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Renaming column for 'Filter.category' to match new field type.
        db.rename_column('issuetracker_filter', 'category', 'category_id')
        # Changing field 'Filter.category'
        db.alter_column('issuetracker_filter', 'category_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issuetracker.IssueCategory'], null=True))

        # Adding index on 'Filter', fields ['category']
        db.create_index('issuetracker_filter', ['category_id'])


    def backwards(self, orm):
        
        # Removing index on 'Filter', fields ['category']
        db.delete_index('issuetracker_filter', ['category_id'])

        # Renaming column for 'Filter.category' to match new field type.
        db.rename_column('issuetracker_filter', 'category_id', 'category')
        # Changing field 'Filter.category'
        db.alter_column('issuetracker_filter', 'category', self.gf('django.db.models.fields.CharField')(max_length=160, null=True))


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
        'auth.user': {
            'Meta': {'object_name': 'User'},
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'issuetracker.externalcasedata': {
            'Meta': {'object_name': 'ExternalCaseData'},
            'doc_id': ('django.db.models.fields.CharField', [], {'default': "'1428045383f04263a5578a0493ebca98'", 'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'21944837bc524b6e8119e60cf2e8f082'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'issue_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'external_data'", 'to': "orm['issuetracker.Issue']"})
        },
        'issuetracker.filter': {
            'Meta': {'object_name': 'Filter'},
            'assigned_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_assigned_to'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issuetracker.IssueCategory']", 'null': 'True', 'blank': 'True'}),
            'closed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_closed_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'closed_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_creator'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'custom_function': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'filter_class': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'filter_module': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'4bd7d23abe3e40a2b764c2958483cc71'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'last_edit_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_last_edit_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'last_edit_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_event_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Actor']", 'null': 'True', 'blank': 'True'}),
            'last_event_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'opened_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_opened_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'opened_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'resolved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_resolved_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'resolved_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'})
        },
        'issuetracker.gridcolumn': {
            'Meta': {'ordering': "('name',)", 'object_name': 'GridColumn'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'column_type': ('django.db.models.fields.CharField', [], {'default': "'case_field'", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'})
        },
        'issuetracker.gridorder': {
            'Meta': {'ordering': "['order']", 'object_name': 'GridOrder'},
            'column': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gridcolumn_displayorder'", 'to': "orm['issuetracker.GridColumn']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'preference': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gridpreference_displayorder'", 'to': "orm['issuetracker.GridPreference']"})
        },
        'issuetracker.gridpreference': {
            'Meta': {'ordering': "['filter']", 'object_name': 'GridPreference'},
            'display_columns': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'display_columns'", 'symmetrical': 'False', 'through': "orm['issuetracker.GridOrder']", 'to': "orm['issuetracker.GridColumn']"}),
            'filter': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'gridpreference'", 'unique': 'True', 'to': "orm['issuetracker.Filter']"}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'4adedb0778c74e98bfaeeb5105f33743'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'sort_columns': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sort_columns'", 'symmetrical': 'False', 'through': "orm['issuetracker.GridSort']", 'to': "orm['issuetracker.GridColumn']"})
        },
        'issuetracker.gridsort': {
            'Meta': {'ordering': "['order']", 'object_name': 'GridSort'},
            'ascending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'column': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gridcolumn_sort'", 'to': "orm['issuetracker.GridColumn']"}),
            'display_split': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'preference': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gridpreference_sort'", 'to': "orm['issuetracker.GridPreference']"})
        },
        'issuetracker.issue': {
            'Meta': {'object_name': 'Issue'},
            'assigned_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issue_assigned_to'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issuetracker.IssueCategory']"}),
            'closed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issue_closed_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'closed_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'7b2d6bd9e6fc4cfb89c8aed5ec385cec'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'last_edit_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issue_last_edit_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'last_edit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'opened_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_opened_by'", 'to': "orm['permissions.Actor']"}),
            'opened_date': ('django.db.models.fields.DateTimeField', [], {}),
            'parent_issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_issues'", 'null': 'True', 'to': "orm['issuetracker.Issue']"}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['patient.Patient']", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'resolved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issue_resolved_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'resolved_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        'issuetracker.issuecategory': {
            'Meta': {'ordering': "['namespace', 'group', 'display']", 'object_name': 'IssueCategory'},
            'display': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'8e1fc1de67a7447c8827eb218aa44e47'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '160', 'null': 'True', 'blank': 'True'})
        },
        'issuetracker.issueevent': {
            'Meta': {'ordering': "['-created_date']", 'object_name': 'IssueEvent'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Actor']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'60eab5a41fec4f0ea3b0433e7eb11f13'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_events'", 'to': "orm['issuetracker.Issue']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_events'", 'null': 'True', 'to': "orm['issuetracker.IssueEvent']"})
        },
        'patient.patient': {
            'Meta': {'object_name': 'Patient'},
            'doc_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'permissions.actor': {
            'Meta': {'ordering': "('created_date',)", 'object_name': 'Actor'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'doc_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['permissions.ActorGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'ee1b1553e9b546a1be3b7188c8b01c9c'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'suspended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'actors'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'permissions.actorgroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ActorGroup'},
            'id': ('django.db.models.fields.CharField', [], {'default': "'77ffa5bdc748447ab6460b081f87f12f'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'})
        }
    }

    complete_apps = ['issuetracker']
