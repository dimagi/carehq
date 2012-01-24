import random
from django.test import TestCase
import hashlib
import uuid
from django.contrib.auth.models import User
from clinical_shared.tests.testcase import CareHQClinicalTestCase
from issuetracker.models import Issue, IssueEvent
from clinical_core.clinical_shared.utils import generator
from issuetracker import issue_constants
from django.core.management import call_command
from issuetracker.models.issuecore import IssueCategory
from permissions.models import Actor, PrincipalRoleRelation, Role
from tenant.models import Tenant


INITIAL_DESCRIPTION = "this is a case made by the test case"
CHANGED_DESCRIPTION = 'i just changed it, foo'


from johnny.cache import invalidate

class EventActivityVerificationTest(CareHQClinicalTestCase):
    fixtures = ['basic_issue_categories']

    def setUp(self):
        self._superSetup()
        Issue.objects.all().delete()
        call_command('carehq_init')
        self.tenant = Tenant.objects.get(name='ASHand')

#    @transaction.commit_manually
#    def tearDown(self):
#        Issue.objects.all().delete()
#        Actor.objects.all().delete()
#        Actor.objects.all().delete()
#        CareTeamMember.objects.all().delete()
#        Patient.objects.all().delete()
#        Category.objects.all().delete()
#        User.objects.all().delete()
#        transaction.commit()

    def testUMLS(self):
        pass
    def testCreateIssueView(self, description = INITIAL_DESCRIPTION):
        """
        In the issue view functions, create an issue
        """
        #self.assertFalse(True)
        pass


    def testCreateIssueApi(self, description=INITIAL_DESCRIPTION):
        """
        Create Issues in the queryset API
        """
        ###########################
        #get the basic counts
        user1 = generator.get_or_create_user()
        user2 = generator.get_or_create_user()

        actor_caregiver = generator.generate_actor(self.tenant, user1, 'caregiver')
        actor_provider = generator.generate_actor(self.tenant, user2, 'provider')

        oldcasecount = Issue.objects.all().count()
        oldevents = IssueEvent.objects.all().count()

        newissue = Issue.objects.new_issue(random.choice(IssueCategory.objects.all()),
                              actor_caregiver.django_actor,
                              description,
                              "mock body %s" % (uuid.uuid4().hex),
                              issue_constants.PRIORITY_MEDIUM,
                              status=issue_constants.ISSUE_STATE_OPEN,
                              activity=issue_constants.ISSUE_EVENT_OPEN
                              )

        #is the thing created?
        self.assertEqual(Issue.objects.all().count(), oldcasecount + 1)
        self.assertEqual(IssueEvent.objects.all().count(), oldevents + 1)
        #verify that the case count created has created a new caseevent
        events = IssueEvent.objects.filter(issue=newissue)
        self.assertEqual(1,events.count())
        #verify that said case count is a new case event of type "open"
        self.assertEqual(issue_constants.ISSUE_EVENT_OPEN, events[0].activity)
        return newissue

    def testIssueModifyClient(self, description = "A test case that modifies a case via the webUI using the web client."):
        #self.assertFalse(True)
        pass


    def testIssueModifyDescriptionApi(self):
        desc= uuid.uuid4().hex
        self.testCreateIssueApi(description=desc)

        user1 = generator.get_or_create_user()
        actor_provider_doc = generator.generate_actor(self.tenant, user1, 'provider')


        issue = Issue.objects.all().get(description=desc)
        issue.description = CHANGED_DESCRIPTION
        issue.last_edit_by = actor_provider_doc.django_actor
        activity = issue_constants.ISSUE_EVENT_EDIT
        issue.save_comment="editing in testIssueModifyDescription"
        issue.save(actor_provider_doc.django_actor, activity=activity)


        events = IssueEvent.objects.filter(issue=issue)
        #we just did an edit, so it should be 2
        self.assertEqual(2, events.count())

        #the top one due to the sort ordering should be the one we just did
        self.assertEqual(issue_constants.ISSUE_EVENT_EDIT, events[0].activity)


        #quickly verify that the original description is still unchanged
        dbissue = Issue.objects.all().get(description=CHANGED_DESCRIPTION)
        self.assertEqual(dbissue.id, issue.id)


    def testIssueCreateChildCases(self):
        self.testCreateIssueApi()
        user1 = generator.get_or_create_user()
        actor_provider_doc = generator.generate_actor(self.tenant, user1, 'provider')

        root_issue = Issue.objects.all().get(description =INITIAL_DESCRIPTION)
        CHILD_ISSUES=10
        for num in range(0,CHILD_ISSUES):
            desc = uuid.uuid4().hex
            subissue = self.testCreateIssueApi(description=desc)
            subissue.parent_issue = root_issue
            subissue.last_edit_by = actor_provider_doc.django_actor
            activity = issue_constants.ISSUE_EVENT_EDIT
            subissue.save_comment="editing in testIssueCreateChildCases"
            subissue.save(actor_provider_doc.django_actor, activity=activity)


        self.assertEqual(root_issue.child_issues.count(), CHILD_ISSUES)






