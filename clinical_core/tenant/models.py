from django.db import models
from django.utils.translation import ugettext_lazy as _
from dimagi.utils import make_uuid
from permissions.models import Actor, ActorGroup

class Tenant(models.Model):
    """
    High level django model for CareHQ tenant.

    Split DB data into separate instances later?
    """
    id = models.CharField(_('Unique tenant ID'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    name = models.CharField(max_length=128, unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    prefix = models.SlugField(max_length=64)
    is_active = models.BooleanField(default=False)


    def __unicode__(self):
        return self.name

class TenantActor(models.Model):
    id = models.CharField(_('Unique Tenant Actor ID'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    actor = models.OneToOneField(Actor, related_name='actor_tenant')
    tenant = models.ForeignKey(Tenant, related_name='tenant_actors')

    class Meta:
        unique_together=('actor', 'tenant')

    def __unicode__(self):
        return "[%s] %s" % (self.tenant, self.actor.name)

class TenantGroup(models.Model):
    id = models.CharField(_('Unique Tenant Actor ID'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    group = models.ForeignKey(ActorGroup, related_name='actorgroup_tenants')
    display = models.CharField(max_length=128, help_text="The displayname of the group within this tenant") #no need to set an additional display name for places where ActorGroup isn't multitenant.
    tenant = models.ForeignKey(Tenant, related_name='tenant_groups')

    class Meta:
        unique_together=('group', 'tenant')

    def __unicode__(self):
        return "[%s] %s" % (self.tenant, self.group.name)
