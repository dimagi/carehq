from quicksect import IntervalNode
from datetime import datetime, timedelta
import time
from pactcarehq import schedule

def get_seconds(d):
    return time.mktime(d.utctimetuple())

def testSimpleIntervals():
    #yesterday, yesteray-year ago
    td_yesterday = timedelta(days=1)
    td_week = timedelta(days=7)
    td_month = timedelta(days=30)
    td_year = timedelta(days=365)

    time_now = datetime.utcnow()
    time_start = time_now - td_year
    time_end = time_now

    time_yesterday = time_now - td_yesterday
    time_week = time_now - td_week
    time_month = time_now - td_month
    time_year = time_now - td_year

    tree = IntervalNode(get_seconds(time_start)-1, get_seconds(time_end)+1)

    tree.insert(get_seconds(time_yesterday), get_seconds(time_now), other="Today")
    tree.insert(get_seconds(time_week), get_seconds(time_yesterday), other ="week-yesterday")
    tree.insert(get_seconds(time_month), get_seconds(time_week), other ="month-week")
    tree.insert(get_seconds(time_year), get_seconds(time_month), other ="year-month")

    res = []
    time_check = time_week
    tree.intersect(get_seconds(time_check)-1, get_seconds(time_check), lambda x: res.append(x.other))
    print res

    #yesterday, day before, day before that, till forever
    #yesterday, day before, nothing



def verify_chw_schedules():
    #username = 'ss524'
    #username = 'rachel'
    #username = 'godfrey'
    #username = 'cs783'
    username = 'lm723'
    #username='nc903'
    #username='lnb9'

    usr_schedule = schedule.get_schedule(username)
    for day in usr_schedule.raw_schedule.keys():
        print "For day: %s" % (day)
        usr_schedule.raw_schedule[day] = sorted(usr_schedule.raw_schedule[day], key=lambda x: x['schedule_index'])
        for item in usr_schedule.raw_schedule[day]:
           start = datetime.strptime(item['active_date'], "%Y-%m-%dT%H:%M:%SZ")
           if item['ended_date'] == None:
               end = datetime.utcnow()
           else:
               end = datetime.strptime(item['ended_date'], "%Y-%m-%dT%H:%M:%SZ")
           print "\t%s: %s From:%s - %s" % (item['schedule_index'], item['pact_id'], start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))



def run():
    verify_chw_schedules()

