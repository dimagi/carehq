from django.contrib.auth.models import User
from django.core.management import call_command
from actorpermission.models import BaseActorDocument, ProviderActor, CHWActor
from carehq_core import carehq_constants, carehq_api
from pactconfig import pact_constants
from pactpatient.models.pactmodels import PactPatient
from patient.models import Patient
from permissions.models import Actor, PrincipalRoleRelation, Role
from nameparser import HumanName
import settings
from tenant.models import Tenant

def run():
    """
    Migration script to turn CHWs into full fledged Providers.

    Also converts existing providers to use the updated role/actor constants.
    This is a migration necessary for the merge of branch chwprovider to develop
    """
    #how it works:
    #iterate through all users.
    #see if the username matches the hack_username chw list.
    #create actors
    #check all patients and see if they are part of the primary_hp or not
    #create a provideractor with permission for that patient.
    hack_usernames = settings.hack_chw_username_phones.keys()
    users = User.objects.all().filter(username__in=hack_usernames)
    total_patients = 0
    seen_doc_ids = set()
    pact_tenant = Tenant.objects.get(name="PACT")

    for u in users:
        django_actors = Actor.objects.all().filter(user=u)
        assignments = PactPatient.get_db().view('pactcarehq/chw_assigned_patients', key=u.username).all()
        patient_doc_ids = [x['id'] for x in assignments]
        django_pts = Patient.objects.filter(doc_id__in=patient_doc_ids)
        [seen_doc_ids.add(x) for x in patient_doc_ids]
        print u.username
        print "\t%d patients" % django_pts.count()
        total_patients += django_pts.count()

        if django_actors.count() == 0:
            print "\tNo actors, need to create one\n"
            chw_actor_doc = CHWActor()
            chw_actor_doc.first_name = u.first_name
            chw_actor_doc.last_name = u.last_name
            chw_actor_doc.title = "PACT CHW"
            chw_actor_doc.phone_number = settings.hack_chw_username_phones[u.username]
            chw_actor_doc.email = u.email
            chw_actor_doc.save(pact_tenant, user=u)
            carehq_api.add_chw(chw_actor_doc)

        else:
            print "\tActors, check for roles and skip"
            chw_actor_doc = django_actors[0].actordoc
        #check all patients to see if they have roles.
        for pt in django_pts:
            print "\tcheck permissions pt: %s" % pt
            careteam_qset = carehq_api.get_careteam(pt.couchdoc)
            print "\tProviders:%s" % careteam_qset
            if careteam_qset.filter(actor=chw_actor_doc.django_actor).count() > 0:
                chw_has_permission=True
            else:
                chw_has_permission=False
            print "\tIs provider accounted for: %s" % chw_has_permission
            if not chw_has_permission:
                carehq_api.set_patient_primary_chw(pt.couchdoc, chw_actor_doc) # or could have iterated over assignments
                print "\tAdded chw actor to patient"
    print "total patients accounted for: %d/%d" % (total_patients, Patient.objects.all().count())

    unassigned_patients = Patient.objects.all().exclude(doc_id__in=list(seen_doc_ids))
    unassigned = [PactPatient.get(x.doc_id) for x in unassigned_patients]
    unassigned_status = [(x.pact_id, x.arm, x.primary_hp) for x in unassigned]
    print unassigned_status


