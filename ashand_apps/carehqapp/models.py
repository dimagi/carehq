import logging
import pdb
import random
from couchdbkit.ext.django.schema import Document, BooleanProperty
from datetime import datetime
from carehqapp.signals import get_assigning_actor
from clinical_shared.manager import patient
from couchforms.models import XFormInstance
from lxml import etree
from issuetracker import issue_constants
from issuetracker.models.issuecore import ExternalIssueData, IssueCategory, Issue
from patient.models import BasePatient, CarehqPatient
import settings
import base64
import uuid

class UsabilitySurvey(Document):
    pass


def get_threshold_category():
    return IssueCategory.objects.get(id='040052ea2029408baf4583a78651635e')


def get_missing_category():
    return IssueCategory.objects.get(id='bddb8723084041238fdda8b37a1c0e35')


class CCDSubmission(XFormInstance):
    is_threshold = BooleanProperty()

    def save(self):
        #do nothing, this is just a wrapper
        pass

    def _get_patient_guid_by_externalid(self):
        external_id = self.form['recordTarget']['patientRole']['id'][1]['@extension']
        patient_docs = CarehqPatient.view('carehqapp/patients_by_externalid', key=external_id).all()
        if len(patient_docs) > 0:
            return patient_docs[0]['id']
        return None


    def get_patient_guid(self):
        if len(self.form['recordTarget']['patientRole']['id']) > 2:
            try:
                b64_doc = self.form['recordTarget']['patientRole']['id'][2]['@extension']
                bytes = base64.b64decode(b64_doc)
                decoded_doc_id = uuid.UUID(bytes=bytes)
                return decoded_doc_id.hex
                #return self.form['recordTarget']['patientRole']['id'][2]['@extension']
            except:
                return self._get_patient_guid_by_externalid()
        else:
            return self._get_patient_guid_by_externalid()


    def ccd_table_data(self):
        return CCDSubmission.find_ccd_table_data(self)

    @staticmethod
    def find_ccd_table_data(xform):
        attachment = xform.fetch_attachment('form.xml', stream=True)
        tree = etree.parse(attachment)
        r = tree.getroot()
        p = r.xpath('//hl7:component/hl7:structuredBody/hl7:component/hl7:section/hl7:text/hl7:table',
            namespaces={'hl7': 'urn:hl7-org:v3'})
        table_fragment = etree.tostring(p[1])
        return table_fragment


    @staticmethod
    def get_raw_answer_data(xform):
        entries_raw = xform.form['component']['structuredBody']['component'][1]['section']['entry']['encounter'][
                      'entryRelationship']
        #entries_raw = filter(lambda x: x.has_key('organizer'), entries_raw)
        answer_arr = []

        for x in entries_raw:
            if not x.has_key('organizer'):
                #this is just the greeting for the session
                #context['entries'].append((x,"No Organizer"))
                continue
            else:
                if isinstance(x['organizer']['component'], list):
                    first_field = x['organizer']['component'][0]['observation']['code']['originalText']
                    first_val = x['organizer']['component'][0]['observation']['value']['@displayName']
                    subarr = []
                    for y in x['organizer']['component'][1:]:
                        field = y['observation']['code']['originalText']
                        val = y['observation']['value']['@displayName']
                        subarr.append({'question': field, 'answer': val})
                    answer_arr.append({'question': first_field, 'answer': first_val, 'branch': subarr})
                elif isinstance(x['organizer']['component'], dict):
                    #the actual guts of the protocols chosen
                    field = x['organizer']['component']['observation']['code']['originalText']
                    val = x['organizer']['component']['observation']['value']['@displayName']
                    answer_arr.append({'question': field, 'answer': val})
        return answer_arr

    @staticmethod
    def get_threshold_violations(xform):
        """
        Return a list of threshold violations with explanation strings.
        """

        violation_frequency = {
            '1': False,
            '2': False,
            '3': True,
            '4': True,
            'More than 4': True,
            }

        sensory_frequency = {
            "Unchanged from last week": False,
            "None": False,
            "Mild": False,
            "Moderate": True,
            "Very Much": True,
            }

        raw_answer_data = CCDSubmission.get_raw_answer_data(xform)

        violations = []
        for x in raw_answer_data:
            if x['question'] == "Have you had diarrhea in the past 24 hours?" and x['answer'].lower() == "yes":
                #check if it's more than three times for diarrhea
                if violation_frequency.get(x['answer'], True):
                    violations.append({"protocol": 'Diarrhea Protocol', "reason" : "More than 3 times in 24 hours"})

            if x['question'] == "Have you vomited in the past 24 hours?" and x['answer'].lower() == "yes":
                #check if it's more than three times for vomiting
                if violation_frequency.get(x['answer'], True):
                    violations.append({"protocol": 'Vomit Protocol', "reason" : "More than 3 times in 24 hours"})

            if x['question'] == "In the past 7 days, have you had any trouble hearing?" and sensory_frequency.get(x['answer'], True):
                    violations.append({"protocol": 'Hearing Protocol', "reason" : "More than a moderate change"})

            if x['question'] == "In the past 7 days, have you felt any joint pain?" and sensory_frequency.get(x['answer'], True):
                violations.append({"protocol": 'Joint Pain Protocol', "reason" : "More than a moderate change"})

            if x['question'] == "In the past 7 days, have you felt any muscle cramps?" and sensory_frequency.get(x['answer'], True):
                violations.append({"protocol": 'Muscle Cramp Protocol', "reason" : "More than a moderate change"})

            if x['question'] == "In the past 7 days, have you felt any numbness in your feet?" and sensory_frequency.get(x['answer'], True):
                violations.append({"protocol": 'Numb Feet Protocol', "reason" : "More than a moderate change"})

            if x['question'] == "In the past 7 days, have you felt any numbness in your hands?" and sensory_frequency.get(x['answer'], True):
                violations.append({"protocol": 'Numb Hand Protocol', "reason" : "More than a moderate change"})

            if x['question'] == "In the past 7 days, have you felt any ringing or buzzing in your ears?" and sensory_frequency.get(x['answer'], True):
                violations.append({"protocol": 'Ringing/buzzing Hearing Protocol', "reason" : "More than a moderate change"})

            if x['question'] == "In the past 7 days, have you felt any tingling in your feet?" and sensory_frequency.get(x['answer'], True):
                violations.append({"protocol": 'Tingling Feet Protocol', "reason" : "More than a moderate change"})

            if x['question'] == "In the past 7 days, have you felt any tingling in your hands?" and sensory_frequency.get(x['answer'], True):
                violations.append({"protocol": 'Tingling Hand Protocol', "reason" : "More than a moderate change"})
        return violations


    @staticmethod
    def check_and_generate_issue(xform, django_patient, mutate_xform=True, skip_if_exists=True):
        """
        form a given xform submission, generate the appropriate issue for threshold violations.
        normallythis should be called from the signals only, but retro checks/tweaks of the protocols should allow for this to be called centrally

        returns nothing
        """

        violations = CCDSubmission.get_threshold_violations(xform)
        new_issue = None

        if ExternalIssueData.objects.filter(doc_id=xform._id).count() > 0 and skip_if_exists:
            return None

        if len(violations) > 0:
            #yes, multiple violations!
            issue_content_body = []

            a = issue_content_body.append
            a("<h3>Reasons</h3>")
            a('<ul>')
            for v in violations:
                a("<li>")
                a("<strong>%s</strong> %s" % (v['protocol'], v['reason']))
                a("</li>")
            a('</ul>')
            a('<hr>')
            a(CCDSubmission.find_ccd_table_data(xform))
            new_issue = Issue.objects.new_issue(
                get_threshold_category(),
                get_system_actor(),
                "Health Session Threshold Violation",
                ''.join(issue_content_body),
                issue_constants.PRIORITY_CHOICES[0][0],
                patient=django_patient,
                status=issue_constants.STATUS_CHOICES[0][0],
                activity=issue_constants.ISSUE_EVENT_CHOICES[0][0],
            )
            #now assign it.
            assign_actor = get_assigning_actor(django_patient)
            if assign_actor is not None:
                new_issue.assign_issue(assign_actor, actor_by=get_system_actor(), commit=True)

            issue_ccd_link = ExternalIssueData()
            issue_ccd_link.issue = new_issue
            issue_ccd_link.doc_id = xform._id
            issue_ccd_link.save()
            xform.is_threshold=True
        else:
            xform.is_threshold=False

        if mutate_xform:
            xform.save()
        return new_issue

    def get_session_time(self):
        return datetime.strptime(self.form['author']['time']['@value'][0:12], '%Y%m%d%H%M')

    def has_issue(self):
        if ExternalIssueData.objects.filter(doc_id=self._id).count() > 0:
            return True
        else:
            return False

    def get_issues(self):
        return Issue.objects.filter(external_data__doc_id=self._id)


    def get_patient_doc(self):
        #patient_doc_id = Patient.objects.get(doc_id=xform.form['recordTarget']['patientRole']['id'][1]['@extension'])
        #patient_doc_id = self.form['recordTarget']['patientRole']['id'][1]['@extension']
        #patient_doc = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_doc_id))

        #hack for testing

        try:
            patient = Patient.objects.get(doc_id=self.get_patient_guid())
            return patient.couchdoc
        except Patient.DoesNotExist:
            logging.error("Error could not match up submission %s with patient with this guid: %s" % (self._id, self.get_patient_guid()))
            return None


from signals import *
