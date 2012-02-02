# -*- coding: utf-8 -*-
import traceback
from couchforms.signals import xform_saved
import logging
import random
import simplejson
from clinical_core.issuetracker.models.issuecore import IssueCategory, Issue
from clinical_core.patient.models import Patient
from issuetracker import issue_constants as caseconstants
from issuetracker.models.issuecore import ExternalIssueData
from permissions.models import Actor
from lxml import etree

def get_ccd_table_data(xform):
    attachment = xform.fetch_attachment('form.xml', stream=True)
    tree = etree.parse(attachment)
    r = tree.getroot()
    p = r.xpath('//hl7:component/hl7:structuredBody/hl7:component/hl7:section/hl7:text/hl7:table', namespaces={'hl7':'urn:hl7-org:v3'})
    table_fragment = etree.tostring(p[1])
    return table_fragment


def get_system_actor():
    return Actor.objects.get(name='System')

def get_threshold_category():
    return IssueCategory.objects.get(id='040052ea2029408baf4583a78651635e')

def process_ccd_submission(sender, xform, **kwargs):
    try:
        #patient = Patient.objects.get(doc_id=xform.form['recordTarget']['patientRole']['id'][1]['@extension'])
        patient = Patient.objects.get(id='d9041f5a3f2a45dba9eba636ce2f0aa8')
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
                get_ccd_table_data(xform),
                random.choice(caseconstants.PRIORITY_CHOICES)[0],
                patient=patient,
                status=caseconstants.STATUS_CHOICES[0][0],
                activity=caseconstants.ISSUE_EVENT_CHOICES[0][0],
            )
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
                get_ccd_table_data(xform),
                random.choice(caseconstants.PRIORITY_CHOICES)[0],
                patient=patient,
                status=caseconstants.STATUS_CHOICES[0][0],
                activity=caseconstants.ISSUE_EVENT_CHOICES[0][0],
            )
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
