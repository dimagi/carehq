# -*- coding: utf-8 -*-
import base64
import logging
import traceback
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
        submit = CCDSubmission.get(xform._id)
        doc_id = xform._id

        #check if it's a resubmit
#        dupes = CCDSubmission.view('carehqapp/ccd_submits_by_session_id', key=xform.form['id']['@root']).count()
#        if dupes > 1:
#            #then this is a dupe/resubmit
#            #change it to dupe
#            xform.doc_type='XFormDuplicate'
#            xform.save()
#            return

        session_id = submit.form['id']['@root']
        #check if it's a resubmit
        sessions = CCDSubmission.view('carehqapp/ccd_submits_by_session_id', key=session_id).all()

        if len(sessions) == 1:
            #if it's one, verify that the id is the same
            session_doc_id = sessions[0]['id']
            if session_doc_id == doc_id:
                #we're good, proceed
                mark_duplicate=False
                pass
            else:
                mark_duplicate=True
        elif len(sessions) == 0:
            mark_duplicate = False
            #it's the first time we're seeing this...or something...though that should never happen
        else:
            #there are mulitple, this is the likely scenario
            mark_duplicate=True

        if mark_duplicate:
            #then this is a dupe/resubmit
            #change it to dupe
            submit.doc_type='XFormDuplicate'
            submit.save()
            return
        else:
            patient = Patient.objects.get(doc_id=submit.get_patient_guid())
            CCDSubmission.check_and_generate_issue(submit, patient)
    except Patient.DoesNotExist:
        logging.error("No patient found on submisison %s" % xform._id)
        return
    except KeyError, ke:
        logging.error("Error accessing ccd keys: %s" % ke)
        return
    except Exception, ex:
        logging.error("Other unknown error trying to get patient guid from ccd: %s" % ex)
        pass

xform_saved.connect(process_ccd_submission)

def issue_save_notification(sender, instance, created, **kwargs):
    issue_update_notifications.delay(instance.issue.id)

post_save.connect(issue_save_notification, sender=IssueEvent)



