from datetime import datetime, timedelta
import random
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from patient.models.patientmodels import BasePatient
from couchdbkit.schema.properties import StringProperty, StringListProperty



form_sequence = [
    'Enrollment',
    'Clinical Info',
    'Clinical Follow Up',
    'Lab Data',
    'Emergency Lab',
    'Biochemical Lab',
    'Speciation',
    'Sensitivity',
    'Outcome',
    ]

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



    def cache_clinical_case(self):
        case = self.latest_case
        submissions = [XFormInstance.get(x) for x in case.xform_ids]

        for s in submissions:
            formname = xmlns_display_map[s.xmlns].replace(' ','_').lower()
            setattr(self, "_%s" % formname, s)
        self._cached_submits=True

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
        if hasattr(self, "_cached_submits"):
            if not self._cached_submits:
                self.cache_clinical_case()
        else:
            self.cache_clinical_case()


        cd4="---"
        if hasattr(self, '_lab_data'):
            if self._lab_data['form'].has_key('hiv_followup'):
                if self._lab_data['form']['hiv_followup']['cdfour'] != '':
                    cd4 = self._lab_data['form']['hiv_followup']['cdfour']
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
    def get_completed_tally(self):
        """
        Returns whether or not patient is active in the study (whether they've been discharged)
        Returns an array with tuples indicating form done-ness along with the submission itself
        """
        case = self.latest_case
        submissions = [XFormInstance.get(x) for x in case.xform_ids]
        keys = xmlns_display_map.keys()
        completed = dict()
        full_len = len(keys)
        for i,s in enumerate(submissions):
            xmlns = s['xmlns']
            displayname = xmlns_display_map[xmlns]
            if xmlns in keys:
                completed[displayname] = (True, s)
                keys.remove(s['xmlns'])


        ret = []
        for n in form_sequence:
            status = completed.get(n, (False, None))
            ret.append((n,status))
        return ret



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
    def get_lab_data(self):
        #get all clinical lab data submissions
        case = self.latest_case
        submissions = [XFormInstance.get(x) for x in case.xform_ids]

        lab_submissions = filter(lambda x: x.xmlns == "http://shine.commcarehq.org/questionnaire/labdata", submissions)
        sorted_labs = sorted(lab_submissions, key=lambda x: x.received_on)
        hiv = ""
        mal_rapid = "" #rapid
        mal_smear = "" #smear
        prophylaxis = ""
        afb_smear = ""
        bloodwbc =dict()
        xray = ""
        hivfollowup = dict()
        bloodcts = dict()

        basic_chemistry = dict()
        lft = dict()

        def fill_sub_dict(submission, key):
            ret_dict = dict()
            for k,v in submission.form[key].items():
                if k not in ret_dict:
                    ret_dict[k] = ''
                stored_val = ret_dict[k]
                if stored_val == "" and v != "":
                    ret_dict[k] = v
            return ret_dict




        for sub in lab_submissions:
            if sub.form['hiv'] != "":
                hiv = sub.form['hiv']
            if sub.form['rapid'] != "":
                mal_rapid = sub.form['rapid']
            if sub.form['smear'] != "":
                mal_smear = sub.form['smear']
            if sub.form['prophylaxis'] != "":
                prophylaxis = sub.form['prophylaxis']
            if sub.form['afb_smear'] != "":
                afb_smear = sub.form['afb_smear']
            if sub.form['xray'] != "":
                if sub.form['xray'] == 'other':
                    if 'xrayother' in sub.form:
                        xray = "Other: %s" % sub.form['xrayother']
                    else:
                        xray='other'
                else:
                    xray = sub.form['xray']

            if 'bloodwbc' in sub.form:
                bloodwbc = fill_sub_dict(sub, 'bloodwbc')
            if 'hivfollowup' in sub.form:
                hivfollowup = fill_sub_dict(sub, 'hivfollowup')
            if 'bloodcts' in sub.form:
                bloodcts = fill_sub_dict(sub, 'bloodcts')

        return [
            ('hiv', { 'hiv test': hiv, 'followup': hivfollowup}),
            ('malaria', {'rapid': mal_rapid, 'smear': mal_smear}),
            ('prophylaxis', prophylaxis),
            ('afb_smear', afb_smear),
            ('xray', xray),
            ('bloodwbc', bloodwbc),
            ('hemogram', bloodcts),
            ('lft', dict()),
        ]




    @property
    def get_current_bed(self):
        if hasattr(self, '_enrollment'):
            return self._enrollment.form['location']['bed']
        else:
            return 'Unknown'

    @property
    def get_current_ward(self):
        if hasattr(self, '_enrollment'):
            return self._enrollment.form['location']['ward']
        else:
            return 'Unknown'



from signals import *
