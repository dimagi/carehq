from casetracker.models import CaseEvent, Case
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta


#get latest case event for case
def get_latest_event(case):
    try:
        return CaseEvent.objects.filter(case=case).order_by('-created_date')#[:1][0]
    except Exception, e:
        #this should never happen as the mere existence of a case should have a case event        
        return None

#for a given set of cases, get all the latest case events.
def get_latest_for_cases(cases_qset, sort=None):
    ret = []
    for case in cases_qset:
        for event in get_latest_event(case):
            ret.append(event)
 #   if sort == "person":
# #       ret.sort(sort_by_person)
#    elif sort == "activity":
#        ret.sort(sort_by_activity)
#    elif sort == "category":
#        ret.sort(sort_by_category)
#    elif sort == "case":
#        ret.sort(sort_by_case)
    return ret

def sort_by_person (a, b):
    return cmp(a.created_by.first_name, b.created_by.first_name)

def sort_by_case (a, b):
    return cmp(a.id, b.id)

def sort_by_activity (a, b):
    return cmp(a.activity.past_tense, b.activity.past_tense)

def sort_by_category (a, b):
    return cmp(a.activity.category.slug, b.activity.category.slug)