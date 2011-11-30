from actorpermission.models.actortypes import BaseActorDocument
from permissions.models import Actor

def run():
    all_actors = BaseActorDocument.view('actorpermission/all_actors', include_docs=True).all()

    dangling = []

    for actor in all_actors:
        print actor._id
        if actor.actor_uuid is None:
            print "\tActor ID is Null"
        try:
            django_actor = Actor.objects.get(id=actor.actor_uuid)
            print "\tActor exists"
        except Actor.DoesNotExist:
            print "\tNo django actor created"
    pass