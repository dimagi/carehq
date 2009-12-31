from casetracker.models import CaseEvent, Case
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta


#get latest case event for case
def get_latest_event(case):
    try:
        return CaseEvent.objects.filter(case=case).order_by('-created_date')[:1][0]        
    except Exception, e:
        #this should never happen as the mere existence of a case should have a case event        
        return None


#for a given set of cases, get all the latest case events.
def get_latest_for_cases(cases_qset):
    ret = []
    for case in cases_qset:
        ret.append(get_latest_event(case))
    return ret