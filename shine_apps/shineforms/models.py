from patient.models.patientmodels import BasePatient
from casexml.apps.phone.models import User
from casexml.apps.case.models import CommCareCase
from casexml.apps.phone.caselogic import case_previously_synced


class ShineUser(User):
    
    def get_open_cases(self, last_sync):
        """
        For now Shine Users all get the same (full) case list.
        """
        return [(case, not case_previously_synced(case.get_id, last_sync))\
                for case in CommCareCase.view("shinepatient/cases_by_patient_id", include_docs=True).all()]
    