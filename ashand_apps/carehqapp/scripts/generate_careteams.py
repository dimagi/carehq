from carehqapp import constants
from issuetracker.models.issuecore import Issue
from clinical_shared.utils import generator
from .demo.demo_careteams import DEMO_CARETEAMS
from patient.models import Patient
from permissions.models import Role, Actor
from tenant.models import Tenant

def run():
    Patient.objects.all().delete()
    Actor.objects.all().delete()
    Issue.objects.all().delete()

    tenant = Tenant.objects.get(name=constants.TENANT_NAME)
    caregiver_role = Role.objects.get(name=constants.role_caregiver)
    provider_role = Role.objects.get(name=constants.role_provider)
    primary_provider_role = Role.objects.get(name=constants.role_primary_provider)
    patient_role=Role.objects.get(name=constants.role_patient)

    for team_dict in DEMO_CARETEAMS:

        #generate patient
        print "############ Generating Patient %s" % (team_dict['patient'])
        patient, caregivers, providers = generator.generate_patient_and_careteam(tenant,
                                                                                 team_dictionary=team_dict,
                                                                                 caregiver_role=caregiver_role,
                                                                                 provider_role=provider_role,
                                                                                 primary_provider_role=provider_role,
                                                                                 patient_role=patient_role)
        patient.mrn = str(generator.random_number())
        patient.save()

        for cg in caregivers:
            print "\tCaregiver %s (%s)" % (cg.name, cg.relation)

        for prov in providers:
            print "\tProvider %s (%s)" % (prov.name, prov.title)

    pass