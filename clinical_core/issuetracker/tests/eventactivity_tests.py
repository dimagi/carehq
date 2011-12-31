#from django.test import TestCase
#from issuetracker.models import ActivityClass
#from issuetracker.models import CASE_EVENT_CHOICES
#class EventActivityVerificationTest(TestCase):
#    fixtures = []
#
#    def setUp(self):
#        pass
#
#    def testVerifyEventActivitiesAreCorrect(self):
#        #A test that verifies that each event activity, it has an appropriate
#        #New Issue, Edit Issue, Resolve Issue, Close Issue, Reopen
#        #and that they are non zero and the special cases are only 1.
#        classes = CASE_EVENT_CHOICES
#        for cat in Category.objects.all():
#            activities = ActivityClass.objects.filter(category=cat)
#            for class_tuple in classes:
#                storage_name = class_tuple[0]
#
#                #first, verify that it even exists
#                totalcount = activities.filter(event_class=storage_name).count()
#                if totalcount == 0:
#                    self.fail("Fixture setup error.  For category %s, there are zero activities of class: %s" % (str(cat), class_tuple[1]))
#
#                #next, if it's open/edit/reopen, we need to make sure there is only one of that type
#                if storage_name == 'event-open' or storage_name == 'event-edit' or storage_name == 'event-reopen':
#                    count = activities.filter(event_class=storage_name).count()
#                    if count != 1:
#                        self.fail("Fixture setup error: %s has been listed twice, it can only exist once per category (%s)" % (class_tuple[0], str(cat)))
#
#
#
#
#
#
