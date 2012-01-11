from couchforms.signals import xform_saved
import logging
import random
import simplejson
from clinical_core.issuetracker.models.issuecore import IssueCategory, Issue
from clinical_core.patient.models.patientmodels import Patient
from issuetracker import constants as caseconstants
from permissions.models import Actor, get_system_actor

def process_ccd_submission(sender, xform, **kwargs):
    try:
        patient = Patient.objects.get(doc_id=xform['recordTarget']['id'][1]['@extension'])
    except Patient.DoesNotExist:
        print "Patient not found!"
        return
    except KeyError:
        print "Malformed submission!"
        return
    try:
        actor = get_system_actor()
    except Actor.DoesNotExist:
        return

    if xform['component']['structuredBody']['component'][1]['section']['entry']['encounter']['entryRelationship']\
            [1]['organizer']['component'][0]['observation']['value']['@displayName']:
        newcase = Issue.objects.new_issue(
            random.choice(IssueCategory.objects.all()),
            actor,
            "Diarrhea threshold violation",
            xform,
            random.choice(caseconstants.PRIORITY_CHOICES)[0],
            patient=patient,
            status=caseconstants.STATUS_CHOICES[0][0],
            activity=caseconstants.CASE_EVENT_CHOICES[0][0],
        )
        newcase.save()

    if xform['component']['structuredBody']['component'][1]['section']['entry']['encounter']['entryRelationship']\
            [2]['organizer']['component'][0]['observation']['value']['@displayName']:
        newcase = Issue.objects.new_issue(
            random.choice(IssueCategory.objects.all()),
            actor,
            "Vomit threshold violation",
            xform,
            random.choice(caseconstants.PRIORITY_CHOICES)[0],
            patient=patient,
            status=caseconstants.STATUS_CHOICES[0][0],
            activity=caseconstants.CASE_EVENT_CHOICES[0][0],
        )
        newcase.save()
        print "Vomit threshold violation"



xform_saved.connect(process_ccd_submission)
