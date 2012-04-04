from casexml.apps.phone.models import User


class ShineUser(User):

    @property
    def raw_username(self):
        return self.username


#    def get_open_cases(self, last_sync):
#        """
#        For now Shine Users all get the same (full) case list.
#        """
#        return [(case, not case_previously_synced(case.get_id, last_sync))\
#                for case in CommCareCase.view("shinepatient/shine_patient_cases", include_docs=True).all()]
    