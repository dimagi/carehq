# -*- coding: utf-8 -*-
import base64
import uuid
from django.db.models.signals import post_save
from carehq_core import carehq_api
from carehq_core.carehq_constants import role_primary_provider, role_provider
from carehqapp.models import CCDSubmission, get_threshold_category
from couchforms.signals import xform_saved
import random
from clinical_core.patient.models import Patient
from issuetracker import issue_constants
from issuetracker.models.issuecore import ExternalIssueData, IssueEvent, Issue
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
    try:
        b64_doc = xform.form['recordTarget']['patientRole']['id'][2]['@extension']
        bytes = base64.b64decode(b64_doc)
        decoded_doc_id = uuid.UUID(bytes=bytes)
        patient = Patient.objects.get(doc_id=decode_doc_id)
        #patient = Patient.objects.get(id='d9041f5a3f2a45dba9eba636ce2f0aa8')
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
        if xform.form['component']['structuredBody']['component'][1]['section']['entry']['encounter']['entryRelationship']\
                [1]['organizer']['component'][0]['observation']['value']['@displayName']:
            new_issue = Issue.objects.new_issue(
                get_threshold_category(),
                system_actor,
                "\tDiarrhea threshold violation",
                CCDSubmission.find_ccd_table_data(xform),
                random.choice(issue_constants.PRIORITY_CHOICES)[0],
                patient=patient,
                status=issue_constants.STATUS_CHOICES[0][0],
                activity=issue_constants.ISSUE_EVENT_CHOICES[0][0],
            )

            #now assign it.
            assign_actor = get_assigning_actor(patient)
            if assign_actor is not None:
                new_issue.assign_issue(assign_actor, actor_by=system_actor, commit=True)


            issue_ccd_link = ExternalIssueData()
            issue_ccd_link.issue = new_issue
            issue_ccd_link.doc_id = xform._id
            issue_ccd_link.save()

            xform.is_threshold=True

    except Exception, ex:
        #tb = traceback.format_exc()
        pass


    try:
        if xform.form['component']['structuredBody']['component'][1]['section']['entry']['encounter']['entryRelationship']\
                [2]['organizer']['component'][0]['observation']['value']['@displayName']:

            new_issue = Issue.objects.new_issue(
                get_threshold_category(),
                system_actor,
                "GI threshold violation",
                CCDSubmission.find_ccd_table_data(xform),
                random.choice(issue_constants.PRIORITY_CHOICES)[0],
                patient=patient,
                status=issue_constants.STATUS_CHOICES[0][0],
                activity=issue_constants.ISSUE_EVENT_CHOICES[0][0],
            )
            #now assign it.
            assign_actor = get_assigning_actor(patient)
            if assign_actor is not None:
                new_issue.assign_issue(assign_actor, actor_by=system_actor, commit=True)

            issue_ccd_link = ExternalIssueData()
            issue_ccd_link.issue = new_issue
            issue_ccd_link.doc_id = xform._id
            issue_ccd_link.save()
            xform.is_threshold=True
            xform.save()
    except Exception, ex:
        #tb = traceback.format_exc()
        #print tb
        pass
    xform.save()


xform_saved.connect(process_ccd_submission)

def issue_save_notification(sender, instance, created, **kwargs):
    issue_update_notifications.delay(instance.issue.id)

post_save.connect(issue_save_notification, sender=IssueEvent)



