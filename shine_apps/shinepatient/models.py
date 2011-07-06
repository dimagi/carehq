from casexml.apps.case.models import CommCareCase
from patient.models.patientmodels import BasePatient
from couchdbkit.schema.properties import StringProperty, BooleanProperty, DateTimeProperty, DateProperty

class ShinePatient(BasePatient):
    """
    A stub implementation of the Patient model
    """
    external_id = StringProperty() #patient_id for human readable
    def is_unique(self):
        return True

    @property
    def view_name(self):
        return "shine_single_patient"


    @property
    def last_activity(self):
        cases = CommCareCase.view("shinepatient/cases_by_patient_guid", key=self._id, include_docs=True).all()
        if len(cases) == 0:
            return "No activity"
        else:
            return cases[0].modified_on


from signals import *