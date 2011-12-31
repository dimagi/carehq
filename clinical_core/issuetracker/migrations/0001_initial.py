# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CaseEvent'
        db.create_table('issuetracker_caseevent', (
            ('id', self.gf('django.db.models.fields.CharField')(default='4c2d846897514cb4ab5d17a10d8cde31', unique=True, max_length=32, primary_key=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(related_name='case_events', to=orm['issuetracker.Issue'])),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('activity', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Actor'])),
            ('parent_event', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_events', null=True, to=orm['issuetracker.CaseEvent'])),
        ))
        db.send_create_signal('issuetracker', ['CaseEvent'])

        # Adding model 'Issue'
        db.create_table('issuetracker_issue', (
            ('id', self.gf('django.db.models.fields.CharField')(default='2bb6b59a3d57420ab977ba0d65bf344d', unique=True, max_length=32, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patient.Patient'], null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('opened_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('opened_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='case_opened_by', to=orm['permissions.Actor'])),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='case_assigned_to', null=True, to=orm['permissions.Actor'])),
            ('assigned_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_edit_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_edit_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='case_last_edit_by', null=True, to=orm['permissions.Actor'])),
            ('resolved_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('resolved_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='case_resolved_by', null=True, to=orm['permissions.Actor'])),
            ('closed_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('closed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='case_closed_by', null=True, to=orm['permissions.Actor'])),
            ('due_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('parent_issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_issues', null=True, to=orm['issuetracker.Issue'])),
        ))
        db.send_create_signal('issuetracker', ['Issue'])

        # Adding model 'ExternalCaseData'
        db.create_table('issuetracker_externalcasedata', (
            ('id', self.gf('django.db.models.fields.CharField')(default='6a580ed7263a4f029c719523a214c3e7', unique=True, max_length=32, primary_key=True)),
            ('case_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='external_data', to=orm['issuetracker.Issue'])),
            ('doc_id', self.gf('django.db.models.fields.CharField')(default='56b0665f2c95479b9992cbbcc5648383', unique=True, max_length=32, db_index=True)),
        ))
        db.send_create_signal('issuetracker', ['ExternalCaseData'])

        # Adding model 'Filter'
        db.create_table('issuetracker_filter', (
            ('id', self.gf('django.db.models.fields.CharField')(default='a2b312485f8e46f8b9593b175e9d11a0', unique=True, max_length=32, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='filter_creator', null=True, to=orm['permissions.Actor'])),
            ('shared', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('custom_function', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filter_module', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('filter_class', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=160, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=160, null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('opened_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='filter_opened_by', null=True, to=orm['permissions.Actor'])),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='filter_assigned_to', null=True, to=orm['permissions.Actor'])),
            ('last_edit_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='filter_last_edit_by', null=True, to=orm['permissions.Actor'])),
            ('resolved_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='filter_resolved_by', null=True, to=orm['permissions.Actor'])),
            ('closed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='filter_closed_by', null=True, to=orm['permissions.Actor'])),
            ('opened_date', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('assigned_date', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('last_edit_date', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('resolved_date', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('closed_date', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('last_event_date', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('last_event_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Actor'], null=True, blank=True)),
        ))
        db.send_create_signal('issuetracker', ['Filter'])

        # Adding model 'GridColumn'
        db.create_table('issuetracker_gridcolumn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=32, db_index=True)),
            ('display', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('column_type', self.gf('django.db.models.fields.CharField')(default='case_field', max_length=16, null=True, blank=True)),
            ('attribute', self.gf('django.db.models.fields.CharField')(max_length=160, null=True, blank=True)),
        ))
        db.send_create_signal('issuetracker', ['GridColumn'])

        # Adding model 'GridSort'
        db.create_table('issuetracker_gridsort', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('column', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gridcolumn_sort', to=orm['issuetracker.GridColumn'])),
            ('preference', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gridpreference_sort', to=orm['issuetracker.GridPreference'])),
            ('ascending', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_split', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('issuetracker', ['GridSort'])

        # Adding model 'GridOrder'
        db.create_table('issuetracker_gridorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('column', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gridcolumn_displayorder', to=orm['issuetracker.GridColumn'])),
            ('preference', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gridpreference_displayorder', to=orm['issuetracker.GridPreference'])),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('issuetracker', ['GridOrder'])

        # Adding model 'GridPreference'
        db.create_table('issuetracker_gridpreference', (
            ('id', self.gf('django.db.models.fields.CharField')(default='4cea16fa97d542a8b81a87515ee607dd', unique=True, max_length=32, primary_key=True)),
            ('filter', self.gf('django.db.models.fields.related.OneToOneField')(related_name='gridpreference', unique=True, to=orm['issuetracker.Filter'])),
        ))
        db.send_create_signal('issuetracker', ['GridPreference'])


    def backwards(self, orm):
        
        # Deleting model 'CaseEvent'
        db.delete_table('issuetracker_caseevent')

        # Deleting model 'Issue'
        db.delete_table('issuetracker_issue')

        # Deleting model 'ExternalCaseData'
        db.delete_table('issuetracker_externalcasedata')

        # Deleting model 'Filter'
        db.delete_table('issuetracker_filter')

        # Deleting model 'GridColumn'
        db.delete_table('issuetracker_gridcolumn')

        # Deleting model 'GridSort'
        db.delete_table('issuetracker_gridsort')

        # Deleting model 'GridOrder'
        db.delete_table('issuetracker_gridorder')

        # Deleting model 'GridPreference'
        db.delete_table('issuetracker_gridpreference')


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
        'issuetracker.caseevent': {
            'Meta': {'ordering': "['-created_date']", 'object_name': 'CaseEvent'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'case_events'", 'to': "orm['issuetracker.Issue']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Actor']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'c1f7ab99699a47bfb0bfcfa522776947'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_events'", 'null': 'True', 'to': "orm['issuetracker.CaseEvent']"})
        },
        'issuetracker.externalcasedata': {
            'Meta': {'object_name': 'ExternalCaseData'},
            'case_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'external_data'", 'to': "orm['issuetracker.Issue']"}),
            'doc_id': ('django.db.models.fields.CharField', [], {'default': "'ebc3a652c12b4fc396727ad1873489bb'", 'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'9f5ec3a7c56b4138911560a25ea49c93'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'issuetracker.filter': {
            'Meta': {'object_name': 'Filter'},
            'assigned_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_assigned_to'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'closed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_closed_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'closed_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter_creator'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'custom_function': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'filter_class': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'filter_module': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'115d5c1d4deb4697a79b5e229586004f'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.CharField', [], {'default': "'c9db20b06a1345ea8d6e12486d3571ba'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
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
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'case_assigned_to'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'closed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'case_closed_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'closed_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'7e540fabdebf4b018b91e8a38e3cf496'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'last_edit_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'case_last_edit_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'last_edit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'opened_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'case_opened_by'", 'to': "orm['permissions.Actor']"}),
            'opened_date': ('django.db.models.fields.DateTimeField', [], {}),
            'parent_issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_issues'", 'null': 'True', 'to': "orm['issuetracker.Issue']"}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['patient.Patient']", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'resolved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'case_resolved_by'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'resolved_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        'patient.patient': {
            'Meta': {'object_name': 'Patient'},
            'doc_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'permissions.actor': {
            'Meta': {'ordering': "('created_date',)", 'object_name': 'Actor'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'doc_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['permissions.ActorGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'f6f4850df0f642a29e5bd8a2b8d7b372'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'suspended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'actors'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'permissions.actorgroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ActorGroup'},
            'id': ('django.db.models.fields.CharField', [], {'default': "'ae72a03e4a704ab5aa04923127fb62f3'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'})
        }
    }

    complete_apps = ['issuetracker']
