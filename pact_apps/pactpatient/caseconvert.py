


#util functions to help convert old CPhone and CAddress stuff to casexml stuff because it's "case updateable"
from casexml.apps.case.models import CommCareCase

def set_address_to_case(django_patient):
    pass

def set_cphones_to_case(django_patient):
    """
    SetAttr all the CPhone objects for a given patient
    """
    couchdoc = django_patient.couchdoc
    case = CommCareCase.get(couchdoc.case_id)
    for i, phone in enumerate(couchdoc.phones):
        #todo: generate XML submissions and submit to site to do case update.
        pass

