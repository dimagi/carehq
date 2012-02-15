from django.core.management import call_command
from actorpermission.models import MachineActor
from permissions.models import Actor
import settings

def run():
    print "make sure you have loaded carehq_core/fixtures/initial_data.json"

    #make an actordoc for the system actor
    sactor = Actor.objects.get(id='43207a2209244ae695850506fff79665')
    if hasattr(sactor, 'actordoc') and sactor.actordoc is not None:
        print "actordoc exists for system actor"
        if sactor.actordoc._id == 'e48f134269884ef3a813d2901cd0f35f':
            print "whew, actordoc matches doc id with fixture"
        else:
            print "wtf, actordoc does NOT match doc id in fixture"
    else:

        ma = MachineActor()
        ma._id = sactor.doc_id
        ma.title =  "CareHQ System Actor"
        ma.first_name = "CareHQ"
        ma.last_name = "CareHQ System"
        ma.email = "ashand-system@dimagi.com"
        ma.actor_uuid = sactor.id
        ma.save(None, user=None)
        print "saved the fixture actor"

    machine_actor = MachineActor.get(sactor.doc_id)
    print machine_actor.django_actor.id == sactor.id




