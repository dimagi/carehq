from carehq_core import carehq_constants
from issuetracker.models.issuecore import Issue
from clinical_shared.utils import generator
from .demo.demo_careteams import DEMO_CARETEAMS
from patient.models import Patient
from permissions.models import Role, Actor
from tenant.models import Tenant

def run():
    """
    Requres carehq_init constants.

    Regenerate a patients with careteams assigned to them (caregivers, providers, etc)

    Note, johnny cache needs to be invalidated or else you're going to see weird behavior in your runserver.  The model changes done here
    are not picked up by memcached or the middleware when the server is running
    """
    Patient.objects.all().delete()
    Actor.objects.all().delete()
    Issue.objects.all().delete()

    tenant = Tenant.objects.get(name='ASHand')
    caregiver_role = Role.objects.get(name=carehq_constants.role_caregiver)
    provider_role = Role.objects.get(name=carehq_constants.role_provider)
    primary_provider_role = Role.objects.get(name=carehq_constants.role_primary_provider)
    patient_role=Role.objects.get(name=carehq_constants.role_patient)

    for team_dict in DEMO_CARETEAMS:

        #generate patient
        print "############ Generating Patient %s" % (team_dict['patient'])
        patient, caregivers, providers = generator.generate_patient_and_careteam(tenant, team_dictionary=team_dict)
        patient.mrn = str(generator.random_number())
        patient.save()

        for cg in caregivers:
            print "\tCaregiver %s (%s)" % (cg.name, cg.relation)

        for prov in providers:
            print "\tProvider %s (%s)" % (prov.name, prov.title)

    pass