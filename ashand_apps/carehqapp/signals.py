# -*- coding: utf-8 -*-
import base64
import uuid
from django.db.models.signals import post_save
from carehq_core import carehq_api
from carehq_core.carehq_constants import role_primary_provider, role_provider
from couchforms.signals import xform_saved
from clinical_core.patient.models import Patient
from issuetracker.models.issuecore import  IssueEvent
from permissions.models import Actor, Role
from tasks import issue_update_notifications


def get_system_actor():
    return Actor.objects.get(name='System')

def get_primary_provider_role():
    return Role.objects.get(name=role_primary_provider)

def get_provider_role():
    return Role.objects.get(name=role_provider)

def get_assigning_actor(patient):
    careteam_dict = carehq_api.get_careteam_dict(patient.couchdoc)
    primary_role = get_primary_provider_role()
    provider_role = get_provider_role()
    if careteam_dict.has_key(primary_role):
        if len(careteam_dict[primary_role]) > 0:
            return careteam_dict[primary_role][0]


    if careteam_dict.has_key(provider_role):
        if len(careteam_dict[provider_role]) > 0:
            return careteam_dict[provider_role][0]
    return None


def process_ccd_submission(sender, xform, **kwargs):
    from carehqapp.models import CCDSubmission
    try:
        b64_doc = xform.form['recordTarget']['patientRole']['id'][2]['@extension']
        bytes = base64.b64decode(b64_doc)
        decoded_doc_id = uuid.UUID(bytes=bytes)
        patient = Patient.objects.get(doc_id=decode_doc_id)
    except Patient.DoesNotExist:
        return
    except KeyError, ke:
        return
    except Exception, ex:
        pass

    try:
        system_actor = get_system_actor()
    except Actor.DoesNotExist:
        return

    #set it as a non threshold violation
    xform.is_threshold=False
    try:
        CCDSubmission.check_and_generate_issue(xform, patient)
    except Exception, ex:
        #tb = traceback.format_exc()
        #print tb
        pass
    xform.save()


xform_saved.connect(process_ccd_submission)

def issue_save_notification(sender, instance, created, **kwargs):
    issue_update_notifications.delay(instance.issue.id)

post_save.connect(issue_save_notification, sender=IssueEvent)



