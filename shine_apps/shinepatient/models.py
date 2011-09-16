from datetime import datetime, timedelta
import random
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from patient.models.patientmodels import BasePatient
from couchdbkit.schema.properties import StringProperty, StringListProperty


xmlns_display_map = {
   'http://shine.commcarehq.org/patient/reg': "Enrollment",
   'http://shine.commcarehq.org/questionnaire/clinical': "Clinical Info",
   'http://shine.commcarehq.org/questionnaire/followup': "Follow Up",
   'http://shine.commcarehq.org/questionnaire/labdata': "Lab Data",
   'http://shine.commcarehq.org/lab/one': "Emergency Lab",
   'http://shine.commcarehq.org/lab/two': "Biochemical Lab",
   'http://shine.commcarehq.org/lab/three': "Speciation",
   'http://shine.commcarehq.org/lab/four': "Sensitivity",
   'http://shine.commcarehq.org/questionnaire/outcome': "Outcome",
}





class ShinePatient(BasePatient):
    """
    A stub implementation of the Patient model
    """
    external_id = StringProperty() #patient_id for human readable

    cases = StringListProperty()


    @property
    def latest_case(self):
        case_docs = [CommCareCase.get(x) for x in self.cases]
        sorted_docs = sorted(case_docs, key=lambda x: x.opened_on)
        return sorted_docs[-1]

    def is_unique(self):
        return True

    @property
    def enrollment_date(self):
        return self.latest_case.opened_on

    @property
    def view_name(self):
        return "shine_single_patient"

    @property
    def get_cd4_count(self):
        case = self.latest_case
        submissions = [XFormInstance.get(x) for x in case.xform_ids]
        cd4=" -- "
        for s in submissions:
            if s.xmlns == 'http://shine.commcarehq.org/questionnaire/labdata':
                if s['form'].has_key('hiv_followup'):
                    if s['form']['hiv_followup']['cdfour'] != '':
                        cd4 = s['form']['hiv_followup']['cdfour']
                        return cd4
        return cd4

    @property
    def get_hiv_status(self):
        case = self.latest_case
        submissions = [XFormInstance.get(x) for x in case.xform_ids]
        hiv ="No"
        for s in submissions:
            if s.xmlns == "http://shine.commcarehq.org/patient/reg":
                if s['form']['hiv_test'] == "yes":
                    return "yes"

            if s.xmlns == 'http://shine.commcarehq.org/questionnaire/labdata':
                if s['form'].has_key('hiv'):
                    hiv = s['form']['hiv']
                    return hiv
        return cd4

    @property
    def get_current_status(self):
        return "Bloodwork > Positive > Lab2"

    @property
    def last_activity(self):
        cases = CommCareCase.view("shinepatient/shine_patient_cases", key=self._id, include_docs=True).all()
        if len(cases) == 0:
            #return "No activity"
            return datetime.mindate
        else:
            return cases[0].modified_on



    @property
    def get_last_action(self):
        case = self.latest_case
        submissions = [XFormInstance.get(x) for x in case.xform_ids]
        xmlns = submissions[-1]['xmlns']
        recv = submissions[-1]['received_on']

        return recv, xmlns_display_map[xmlns]

    @property
    def get_current_status(self):
        """
        Returns whether or not patient is active in the study (whether they've been discharged)
        """
        case = self.latest_case
        submissions = [XFormInstance.get(x) for x in case.xform_ids]
        keys = xmlns_display_map.keys()
        full_len = len(keys)
        for i,s in enumerate(submissions):
            if s['xmlns'] in keys:
                keys.remove(s['xmlns'])
        if len(keys) != 0:
            return "%d/%d" % (full_len-len(keys), full_len)
        else:
            return "[Done]"

    @property
    def data_complete(self):
        """
        todo: Do an analysis of all the fields collected in all forms to determine if dataset is complete
        """
        return random.choice([True, False])

    @property
    def is_positive(self):
        """
        Determine positivity from submitted form TODO
        """
        return random.choice([True, False])



    @property
    def get_current_bed(self):
        return "5e"

    @property
    def get_current_ward(self):
        return 3


from signals import *
