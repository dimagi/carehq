from carehq_core import carehq_constants
from carehqapp.scripts.study import study_id_list
from clinical_shared.utils.generator import get_or_create_user
from issuetracker.models.issuecore import Issue
from clinical_shared.utils import generator
from .demo.demo_careteams import DEMO_CARETEAMS
from patient.models import Patient, CarehqPatient
from permissions.models import Role, Actor
from tenant.models import Tenant

def run():
    """
    Requres carehq_init constants.

    Regenerate a patients with careteams assigned to them (caregivers, providers, etc)

    Note, johnny cache needs to be invalidated or else you're going to see weird behavior in your runserver.  The model changes done here
    are not picked up by memcached or the middleware when the server is running
    """
    #Patient.objects.all().delete()
    #Actor.objects.all().delete()
    #Issue.objects.all().delete()

    tenant = Tenant.objects.get(name='ASHand')
    caregiver_role = Role.objects.get(name=carehq_constants.role_caregiver)
    patient_role = Role.objects.get(name=carehq_constants.role_patient)

    for num, study_pt_dict in enumerate(study_id_list):


        print "############ Generating Patient %s" % study_pt_dict['external_id']

        pt_doc_id = study_pt_dict['patient_guid']
        first_name = "Ashand"
        last_name = study_pt_dict['external_id']
        study_id = study_pt_dict['external_id']
        sim_phone = study_pt_dict['sim_phone']

        try:
            CarehqPatient.get_db().delete_doc(pt_doc_id)
        except:
            pass

        ptuser = get_or_create_user(first_name=first_name, last_name=last_name)
        patient_doc = generator.get_or_create_patient(tenant,
            user=ptuser,
            first_name=first_name,
            middle_name='',
            last_name=last_name,
            gender='f',
            id_override=pt_doc_id)

        patient_doc.study_id = study_id
        patient_doc.sim_number = sim_phone
        patient_doc.save()

        generator.get_or_create_actor(tenant, )
    pass