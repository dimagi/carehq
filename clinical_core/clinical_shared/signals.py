from functools import partial
import pdb
from django.db.models.signals import post_init
from carehq_core import carehq_api
from patient.models import Patient

def _get_careteam(django_patient):
    pass

def _add_caregiver(django_patient, caregiver_actor_doc):
    pass

def _add_provider(django_patient, actor_doc, role):
    pass

def _get_providers(django_patient):
    provider_prrs = carehq_api.get_patient_providers(django_patient.couchdoc)
    return [x.actor for x in provider_prrs]

def _get_caregivers(django_patient):
    caregiver_prrs = carehq_api.get_patient_caregivers(django_patient.couchdoc)
    return [x.actor for x in caregiver_prrs]

def patient_post_init(sender, instance, *args, **kwargs):
    doc_id = instance.doc_id
    #setattr(instance, 'add_provider', partial(_get_careteam, instance.couchdoc))
    if doc_id is not None:
        #doc = BaseActorDocument.view('actorpermission/all_actors',key=doc_id, include_docs=True).first()
        setattr(instance, 'get_caregivers', partial(_get_caregivers, instance))
        setattr(instance, 'get_providers', partial(_get_providers, instance))

post_init.connect(patient_post_init, sender=Patient)