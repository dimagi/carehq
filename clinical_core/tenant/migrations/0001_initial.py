# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Tenant'
        db.create_table('tenant_tenant', (
            ('id', self.gf('django.db.models.fields.CharField')(default='42eb137979054abc8ef4b40ffffb6a54', unique=True, max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, db_index=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('prefix', self.gf('django.db.models.fields.SlugField')(max_length=64, db_index=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('tenant', ['Tenant'])

        # Adding model 'TenantActor'
        db.create_table('tenant_tenantactor', (
            ('id', self.gf('django.db.models.fields.CharField')(default='a7372f3299d04cd382b9eada9955077a', unique=True, max_length=32, primary_key=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actor_tenants', to=orm['permissions.Actor'])),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tenant_actors', to=orm['tenant.Tenant'])),
        ))
        db.send_create_signal('tenant', ['TenantActor'])

        # Adding unique constraint on 'TenantActor', fields ['actor', 'tenant']
        db.create_unique('tenant_tenantactor', ['actor_id', 'tenant_id'])

        # Adding model 'TenantGroup'
        db.create_table('tenant_tenantgroup', (
            ('id', self.gf('django.db.models.fields.CharField')(default='bf906933a9cb424b99a81daa6fdc2ede', unique=True, max_length=32, primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actorgroup_tenants', to=orm['permissions.ActorGroup'])),
            ('display', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tenant_groups', to=orm['tenant.Tenant'])),
        ))
        db.send_create_signal('tenant', ['TenantGroup'])

        # Adding unique constraint on 'TenantGroup', fields ['group', 'tenant']
        db.create_unique('tenant_tenantgroup', ['group_id', 'tenant_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'TenantGroup', fields ['group', 'tenant']
        db.delete_unique('tenant_tenantgroup', ['group_id', 'tenant_id'])

        # Removing unique constraint on 'TenantActor', fields ['actor', 'tenant']
        db.delete_unique('tenant_tenantactor', ['actor_id', 'tenant_id'])

        # Deleting model 'Tenant'
        db.delete_table('tenant_tenant')

        # Deleting model 'TenantActor'
        db.delete_table('tenant_tenantactor')

        # Deleting model 'TenantGroup'
        db.delete_table('tenant_tenantgroup')


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
        'permissions.actor': {
            'Meta': {'ordering': "('created_date',)", 'object_name': 'Actor'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'doc_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['permissions.ActorGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'315a771335744fa18dc4dc8107206c28'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'suspended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'actors'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'permissions.actorgroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ActorGroup'},
            'id': ('django.db.models.fields.CharField', [], {'default': "'94049082d6414715a5d1fba105cc8f12'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'})
        },
        'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'93723dfa910e445cbbce6b3b77c816e2'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'prefix': ('django.db.models.fields.SlugField', [], {'max_length': '64', 'db_index': 'True'})
        },
        'tenant.tenantactor': {
            'Meta': {'unique_together': "(('actor', 'tenant'),)", 'object_name': 'TenantActor'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actor_tenants'", 'to': "orm['permissions.Actor']"}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'4b0b3ff643114297b0988ad90b3c7779'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tenant_actors'", 'to': "orm['tenant.Tenant']"})
        },
        'tenant.tenantgroup': {
            'Meta': {'unique_together': "(('group', 'tenant'),)", 'object_name': 'TenantGroup'},
            'display': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actorgroup_tenants'", 'to': "orm['permissions.ActorGroup']"}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'19bf664c977b4e1589f8ea0b5e60d373'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tenant_groups'", 'to': "orm['tenant.Tenant']"})
        }
    }

    complete_apps = ['tenant']
