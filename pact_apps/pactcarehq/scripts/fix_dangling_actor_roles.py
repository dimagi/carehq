from actorpermission.models import  ProviderActor
import permissions
from permissions.models import Actor, Role, PrincipalRoleRelation
from tenant.models import Tenant

def run():
    all_actors = ProviderActor.view('actorpermission/all_actors', include_docs=True).all()

    pact_tenant = Tenant.objects.get(name="PACT")
    dangling = []

    for actor in all_actors:
        print "%s: %s" % (actor.doc_type, actor._id)
        if actor.actor_uuid is None:
            print "\tActor ID is Null, skipping"
        try:
            django_actor = Actor.objects.get(id=actor.actor_uuid)
            print "\tActor exists, setting role"
            role_class = Role.objects.get(name=carehq_constants.role_external_provider)

            prrs = PrincipalRoleRelation.objects.filter(role=role_class, actor=django_actor, content_id=None)
            if prrs.count() == 0:
                print "\tMissing Role for actor, setting"
                permissions.utils.add_role(django_actor, role_class)
            else:
                print "\tRole found, done."
        except Actor.DoesNotExist:
            print "\tNo django actor created"
            actor.actor_uuid = None
            actor.save(pact_tenant)
    pass