from django.contrib.auth.models import User
from actorpermission.models.actortypes import BaseActorDocument, ProviderActor, CHWActor
from pactpatient.models.pactmodels import PactPatient
from patient.models.patientmodels import Patient
from permissions.models import Actor
from nameparser import HumanName
import settings
from tenant.models import Tenant

def run():
    """
    Migration script to turn CHWs into full fledged Providers.
    """


    #how it works:
    #iterate through all users.
    #see if the username matches the hack_username chw list.
    #create actors
    #check all patients and see if they are part of the primary_hp or not
    #create a provideractor with permission for that patient.

    #actors = Actor.objects.all()

    hack_usernames = settings.hack_chw_username_phones.keys()
    users = User.objects.all().filter(username__in=hack_usernames)
    total_patients = 0
    seen_doc_ids = set()
    pact_tenant = Tenant.objects.get(name="PACT")

    for u in users:
        actors = Actor.objects.all().filter(user=u)
        assignments = PactPatient.get_db().view('pactcarehq/chw_assigned_patients', key=u.username).all()
        patient_doc_ids = [x['id'] for x in assignments]
        django_pts = Patient.objects.filter(doc_id__in=patient_doc_ids)
        [seen_doc_ids.add(x) for x in patient_doc_ids]
        print u.username
        print "\t%d patients" % django_pts.count()
        total_patients += django_pts.count()

        if actors.count() == 0:
            print "\tNo actors, need to create one\n"
            chw_actor = CHWActor()
            chw_actor.first_name = u.first_name
            chw_actor.last_name = u.last_name
            chw_actor.title = "PACT CHW"
            chw_actor.phone_number = settings.hack_chw_username_phones[u.username]
            chw_actor.save(pact_tenant, user=u)
            carehq_api.add_chw(chw_actor)

        else:
            print "\tActors, check for roles and skip"
            chw_actor = actors[0]
        #check all patients to see if they have roles.
        for pt in django_pts:
            print "\tcheck permissions pt: %s" % pt
            careteam_qset = carehq_api.get_careteam(pt)
            print "\tProviders:%s" % careteam_qset
            if careteam_qset.filter(actor=chw_actor.django_actor).count() > 0:
                chw_has_permission=True
            else:
                chw_has_permission=False
            print "\tIs provider accounted for: %s" % chw_has_permission
            if not chw_has_permission:
                carehq_api.set_patient_primary_chw(pt.couchdoc, chw_actor) # or could have iterated over assignments
                print "\tAdded chw actor to patient"


    print "total patients accounted for: %d/%d" % (total_patients, Patient.objects.all().count())

    unassigned_patients = Patient.objects.all().exclude(doc_id__in=list(seen_doc_ids))
    unassigned = [PactPatient.get(x.doc_id) for x in unassigned_patients]
    unassigned_status = [(x.pact_id, x.arm, x.primary_hp) for x in unassigned]
    print unassigned_status

#
#    raw_docs = BaseActorDocument.view('actorpermission/all_actors', include_docs=True).all()
#    pact_tenant = Tenant.objects.get(name="PACT")
#
#    for r in raw_docs:
#        try:
#            actor_doc = BaseActorDocument.get_typed_from_id(r._id)
#            raw_name = actor_doc.name
#            parsed_name = HumanName(raw_name)
#            #print parsed_name.title
#            if isinstance(actor_doc, ProviderActor):
#                #set the old title to the new provider_title
#                actor_doc.provider_title = actor_doc.title
#
#            print "%s: %s" % (raw_name, list(parsed_name))
#            if len(parsed_name.title) > 0:
#                print "\tTitles: %s" % parsed_name.title
#                actor_doc.title=parsed_name.title
#
#
#            print "\tFirst: %s" % parsed_name.first
#
#
#
#
#
#            if len(parsed_name.middle) > 0:
#                print "\tMiddle: %s" % parsed_name.middle
#                actor_doc.first_name = "%s %s" % (parsed_name.first, parsed_name.middle.replace('.',''))
#            else:
#                actor_doc.first_name = parsed_name.first
#
#            print "\tLast: %s" % parsed_name.last
#
#            if len(parsed_name.suffix) > 0:
#                print "\tSuffix: %s" % parsed_name.suffix
#                actor_doc.last_name = "%s %s" % (parsed_name.last, parsed_name.suffix)
#            else:
#                actor_doc.last_name = parsed_name.last
#            #print "%s: %s, %s\n" % (raw_name, parsed_name.last, parsed_name.first)
#            delattr(actor_doc,'name')
#            actor_doc.save(pact_tenant)
#        except Exception, ex:
#            print "Error: %s" % ex
