# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'IssueCategory'
        db.create_table('issuetracker_issuecategory', (
            ('id', self.gf('django.db.models.fields.CharField')(default='bbb0fb7645dc4f9d94cd1a5b69e799d3', unique=True, max_length=32, primary_key=True)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('display', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('namespace', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=160, null=True, blank=True)),
        ))
        db.send_create_signal('issuetracker', ['IssueCategory'])

        # Adding model 'IssueEvent'
        db.create_table('issuetracker_issueevent', (
            ('id', self.gf('django.db.models.fields.CharField')(default='eb9c8b255ed54e15aecebdb2113fbc3e', unique=True, max_length=32, primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='issue_events', to=orm['issuetracker.Issue'])),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('activity', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Actor'])),
            ('parent_event', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_events', null=True, to=orm['issuetracker.IssueEvent'])),
        ))
        db.send_create_signal('issuetracker', ['IssueEvent'])

        # Adding model 'Issue'
        db.create_table('issuetracker_issue', (
            ('id', self.gf('django.db.models.fields.CharField')(default='c0bb6c1dc7684990b9a96f62ff35dbc6', unique=True, max_length=32, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issuetracker.IssueCategory'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patient.Patient'], null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('opened_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('opened_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='issue_opened_by', to=orm['permissions.Actor'])),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issue_assigned_to', null=True, to=orm['permissions.Actor'])),
            ('assigned_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_edit_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_edit_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issue_last_edit_by', null=True, to=orm['permissions.Actor'])),
            ('resolved_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('resolved_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issue_resolved_by', null=True, to=orm['permissions.Actor'])),
            ('closed_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('closed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issue_closed_by', null=True, to=orm['permissions.Actor'])),
            ('due_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('parent_issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_issues', null=True, to=orm['issuetracker.Issue'])),
        ))
        db.send_create_signal('issuetracker', ['Issue'])

        # Adding model 'ExternalCaseData'
        db.create_table('issuetracker_externalcasedata', (
            ('id', self.gf('django.db.models.fields.CharField')(default='47b9ec60e97c47978587bcdb8c6bf751', unique=True, max_length=32, primary_key=True)),
            ('issue_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='external_data', to=orm['issuetracker.Issue'])),
            ('doc_id', self.gf('django.db.models.fields.CharField')(default='d3c0f7d9d14a4adfa47efd516f615926', unique=True, max_length=32, db_index=True)),
        ))
        db.send_create_signal('issuetracker', ['ExternalCaseData'])

        # Adding model 'Filter'
        db.create_table('issuetracker_filter', (
            ('id', self.gf('django.db.models.fields.CharField')(default='e5fd5bf02299499c8112b40894a25f91', unique=True, max_length=32, primary_key=True)),
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
            ('id', self.gf('django.db.models.fields.CharField')(default='2f0119513fc649dcaabbc4d398c639f6', unique=True, max_length=32, primary_key=True)),
            ('filter', self.gf('django.db.models.fields.related.OneToOneField')(related_name='gridpreference', unique=True, to=orm['issuetracker.Filter'])),
        ))
        db.send_create_signal('issuetracker', ['GridPreference'])


    def backwards(self, orm):
        
        # Deleting model 'IssueCategory'
        db.delete_table('issuetracker_issuecategory')

        # Deleting model 'IssueEvent'
        db.delete_table('issuetracker_issueevent')

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
        'issuetracker.externalcasedata': {
            'Meta': {'object_name': 'ExternalCaseData'},
            'doc_id': ('django.db.models.fields.CharField', [], {'default': "'f21f27c553cb4a338bb09ca46c2c6c17'", 'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'8df92c0ea86841358e9834dade8eb683'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'issue_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'external_data'", 'to': "orm['issuetracker.Issue']"})
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
            'id': ('django.db.models.fields.CharField', [], {'default': "'8e1b9fc421db41769ef3527536ffc887'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.CharField', [], {'default': "'db13c3c2c45746669da98819d953e985'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.CharField', [], {'default': "'03be726fd75f405396c8f29e40fed56e'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
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
            'Meta': {'ordering': "['-display']", 'object_name': 'IssueCategory'},
            'display': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'d7cbd37f635f4a00bbb62ca414b1292b'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '160', 'null': 'True', 'blank': 'True'})
        },
        'issuetracker.issueevent': {
            'Meta': {'ordering': "['-created_date']", 'object_name': 'IssueEvent'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Actor']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'df17374acb6a4be9bdcd52c913885f02'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_events'", 'to': "orm['issuetracker.Issue']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_events'", 'null': 'True', 'to': "orm['issuetracker.IssueEvent']"})
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
            'id': ('django.db.models.fields.CharField', [], {'default': "'95efcd268dcf4d45a9be74596fd09fb2'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'suspended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'actors'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'permissions.actorgroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ActorGroup'},
            'id': ('django.db.models.fields.CharField', [], {'default': "'659e1b57fe0d4b02bb3d44b339ec2f7c'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'})
        }
    }

    complete_apps = ['issuetracker']
