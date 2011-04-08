#Determine the schedule for a CHW for a given date.
from patient.models.couchmodels import CPatient


#interval trees:
#by chw
#by day of week
#then get the intervals

#so for a query, you have a given date and chw
#for that given day of the week, then check the interval
from datetime import datetime, timedelta, timedelta
import time
from quicksect import IntervalNode
import simplejson

cached_schedules = {}

def get_seconds(d):
    return time.mktime(d.utctimetuple())

class CHWPatientSchedule(object):
    def __init__(self, username, intervaltrees, raw_schedule):
        self.username=username
        self.intervals = intervaltrees
        self.raw_schedule = raw_schedule
        #print "create for username %s" % (username)
    def get_scheduled(self, date_val):
        """
        For a given date, return the array of pact_ids that are scheduled for visiting.  This will check the activate date by using the internal interval tree.
        Parameter:  datetime value
        Returns: array of pact_ids
        """
        #tree.intersect(get_seconds(time_check)-1, get_seconds(time_check), lambda x: res.append(x.other))
        day_of_week = date_val.isoweekday() % 7
        if not self.intervals.has_key(day_of_week):
            return []
        else:
            #print 'has key for this day of the week %d' % (day_of_week)
            pass
        day_tree = self.intervals[day_of_week]
        results=[]
        day_tree.intersect(get_seconds(date_val)-.1, get_seconds(date_val), lambda x:results.append(x.other))
        return results

def get_schedule(chw_username, override_date = None):
    #print "doing schedule lookup for %s" % (chw_username)
    if cached_schedules.has_key(chw_username):
        return cached_schedules[chw_username]
    if override_date == None:
        nowdate = datetime.utcnow()
    else:
        nowdate = override_date
    db = CPatient.get_db()
    chw_schedules = db.view('pactcarehq/chw_dot_schedule_condensed', key=chw_username).all()
    day_intervaltree = {}

    for item in chw_schedules:
        single_sched = item['value']
        #print "Iterating single schedule %s" % (single_sched)
        day_of_week = int(single_sched['day_of_week'])
        if day_intervaltree.has_key(day_of_week):
            daytree = day_intervaltree[day_of_week]
        else:
            daytree = IntervalNode(get_seconds(datetime.min), get_seconds(nowdate + timedelta(days=10)))

        if single_sched['ended_date'] == None:
            enddate = nowdate+timedelta(days=9)
        else:
            enddate = datetime.strptime(single_sched['ended_date'], "%Y-%m-%dT%H:%M:%SZ")
            #enddate = single_sched['ended_date']

        startdate = datetime.strptime(single_sched['active_date'], "%Y-%m-%dT%H:%M:%SZ")
        #startdate = single_sched['active_date']
        pact_id = single_sched['pact_id']
        
        daytree.insert(get_seconds(startdate), get_seconds(enddate), other=pact_id)
        day_intervaltree[day_of_week] = daytree


    cached_schedules[chw_username] = CHWPatientSchedule(chw_username, day_intervaltree, chw_schedules)
    return cached_schedules[chw_username]

