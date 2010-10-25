from dotsview.models import Observation
from patient.models.djangomodels import Patient
from patient.models.couchmodels import CPatient
from django.contrib.auth.models import User

def process_dots_json(doc, dots_json):
    username = doc['form']['Meta']['username']
    user = User.objects.get(username=username)
    #kinda nasty but get the pact_id for patient lookup
    patient_doc = CPatient.view('pactcarehq/patient_pactids', key=doc['form']['pact_id']).first()
    pt = Patient.objects.get(doc_id=patient_doc._id)
    return Observation.from_json(dots_json, pt, user, doc) #provider=provider_actor, patient=pt, json=dots_json)