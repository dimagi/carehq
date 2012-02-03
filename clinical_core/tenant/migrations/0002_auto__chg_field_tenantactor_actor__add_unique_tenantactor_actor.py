# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'TenantActor.actor'
        db.alter_column('tenant_tenantactor', 'actor_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['permissions.Actor']))

        # Adding unique constraint on 'TenantActor', fields ['actor']
        db.create_unique('tenant_tenantactor', ['actor_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'TenantActor', fields ['actor']
        db.delete_unique('tenant_tenantactor', ['actor_id'])

        # Changing field 'TenantActor.actor'
        db.alter_column('tenant_tenantactor', 'actor_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Actor']))


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
            'id': ('django.db.models.fields.CharField', [], {'default': "'72748b5d7d31456e9b20bde23b074e19'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'suspended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'actors'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'permissions.actorgroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ActorGroup'},
            'id': ('django.db.models.fields.CharField', [], {'default': "'f6f68489b1d04bf390bf4abc948c7250'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'})
        },
        'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'d5891d1a584645c7a43e1cf90fef738c'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'prefix': ('django.db.models.fields.SlugField', [], {'max_length': '64', 'db_index': 'True'})
        },
        'tenant.tenantactor': {
            'Meta': {'unique_together': "(('actor', 'tenant'),)", 'object_name': 'TenantActor'},
            'actor': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'actor_tenant'", 'unique': 'True', 'to': "orm['permissions.Actor']"}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'03c64b4420ab408b9e72bc3478502f23'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tenant_actors'", 'to': "orm['tenant.Tenant']"})
        },
        'tenant.tenantgroup': {
            'Meta': {'unique_together': "(('group', 'tenant'),)", 'object_name': 'TenantGroup'},
            'display': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actorgroup_tenants'", 'to': "orm['permissions.ActorGroup']"}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'e97005305ec84fa6bded6f84a9fda0fe'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tenant_groups'", 'to': "orm['tenant.Tenant']"})
        }
    }

    complete_apps = ['tenant']
