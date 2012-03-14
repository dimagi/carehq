from actorpermission.models import  ProviderActor
from permissions.models import Actor
from tenant.models import Tenant

def run():
    all_actors = ProviderActor.view('actorpermission/all_actors', include_docs=True).all()

    pact_tenant = Tenant.objects.get(name="PACT")
    dangling = []

    for actor in all_actors:
        print "%s: %s" % (actor.doc_type, actor._id)
        if actor.actor_uuid is None:
            print "\tActor ID is Null"
        try:
            django_actor = Actor.objects.get(id=actor.actor_uuid)
            print "\tActor exists"
        except Actor.DoesNotExist:
            print "\tNo django actor created"
            #first see if doc_id exists.
            doc_id_exists = Actor.objects.filter(doc_id=actor._id)
            if doc_id_exists.count() > 0:
                existing_actor = doc_id_exists[0]
                actor.actor_uuid = existing_actor.id
                actor.save(pact_tenant)
            else:
                #create a NEW django actor paired with this actordoc
                actor.actor_uuid = None
                actor.save(pact_tenant)
    pass