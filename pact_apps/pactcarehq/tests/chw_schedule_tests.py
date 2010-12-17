from django.test import TestCase
from quicksect import IntervalNode
from datetime import datetime, timedelta


def report_schedule(node):
    print node.other

class BasicCaseTests(TestCase):
    def setUp(self):
        pass

    def testSimpleIntervals(self):
        #yesterday, yesteray-year ago
        td_yesterday = timedelta(days=1)
        td_year = timedelta(days=365)
        time_now = datetime.utcnow()

        time_start = datetime.utcnow() - td_year
        time_end = datetime.utcnow()

        time_yesterday = datetime.utcnow() - td_yesterday
        
        tree = IntervalNode(time_start.toordinal(), time_end.toordinal())

        tree.insert(time_yesterday.toordinal(), time_now.toordinal(), other="From Yesterday")
        tree.insert((time_yesterday - timedelta(days=7)).toordinal(), time_yesterday.toordinal(), other ="Yesterday, week")
        tree.insert(time_start.toordinal(), (time_yesterday - timedelta(days=7)).toordinal(), other ="Yesterday, week")

        tree.intersect(time_now.utcnow().toordinal(), time_now.utcnow().toordinal(), report_schedule)



        #yesterday, day before, day before that, till forever

        #yesterday, day before, nothing

        pass



