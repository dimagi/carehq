#Determine the schedule for a CHW for a given date.


#interval trees:
#by chw
#by day of week
#then get the intervals

#so for a query, you have a given date and chw
#for that given day of the week, then check the interval
from datetime import datetime, timedelta, timedelta
import time
from quicksect import IntervalNode
from django.core.cache import cache
import simplejson
from pactpatient.models.pactmodels import PactPatient

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
    cached_schedules = cache.get("%s_schedule" % (chw_username), None)

    if override_date == None:
        nowdate = datetime.now()
    else:
        nowdate = override_date

    day_intervaltree = {}
    if cached_schedules == None:
        #no documents, then we need to load them up
        db = PactPatient.get_db()
        chw_schedules = db.view('pactcarehq/chw_dot_schedule_condensed', key=chw_username).all()
        to_cache = []
        for item in chw_schedules:
            single_sched = item['value']
            to_cache.append(single_sched)
        cache.set("%s_schedule" % (chw_username), simplejson.dumps(to_cache), 3600)
        cached_arr = to_cache
    else:
        cached_arr = simplejson.loads(cached_schedules)

    for single_sched in cached_arr:
        day_of_week = int(single_sched['day_of_week'])
        if day_intervaltree.has_key(day_of_week):
            daytree = day_intervaltree[day_of_week]
        else:
            #if there's no day of week indication for this, then it's just a null interval node.  To start this node, we make it REALLY old.
            daytree = IntervalNode(get_seconds(datetime.min), get_seconds(nowdate + timedelta(days=10)))
        if single_sched['ended_date'] == None:
            enddate = nowdate+timedelta(days=9)
        else:
            enddate = datetime.strptime(single_sched['ended_date'], "%Y-%m-%dT%H:%M:%SZ")

        startdate = datetime.strptime(single_sched['active_date'], "%Y-%m-%dT%H:%M:%SZ")
        pact_id = single_sched['pact_id']

        daytree.insert(get_seconds(startdate), get_seconds(enddate), other=pact_id)
        day_intervaltree[day_of_week] = daytree



    #cached_schedules[chw_username] = CHWPatientSchedule(chw_username, day_intervaltree, chw_schedules)
    #return cached_schedules[chw_username]
    return CHWPatientSchedule(chw_username, day_intervaltree, cached_arr)

