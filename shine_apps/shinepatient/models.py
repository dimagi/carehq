from datetime import datetime, timedelta
from casexml.apps.case.models import CommCareCase
from patient.models.patientmodels import BasePatient
from couchdbkit.schema.properties import StringProperty, StringListProperty

class ShinePatient(BasePatient):
    """
    A stub implementation of the Patient model
    """
    external_id = StringProperty() #patient_id for human readable

    cases = StringListProperty()

    def is_unique(self):
        return True

    @property
    def view_name(self):
        return "shine_single_patient"

    @property
    def get_cd4_count(self):
        return 100

    @property
    def get_hiv_status(self):
        return True

    @property
    def get_current_status(self):
        return "Bloodwork > Positive > Lab2"

    @property
    def get_enrollment_date(self):
        return datetime.utcnow() - timedelta(days=5)

    @property
    def last_activity(self):
        cases = CommCareCase.view("shinepatient/shine_patient_cases", key=self._id, include_docs=True).all()
        if len(cases) == 0:
            #return "No activity"
            return datetime.mindate
        else:
            return cases[0].modified_on

    @property
    def get_current_bed(self):
        return "5e"

    @property
    def get_current_ward(self):
        return 3

from signals import *
