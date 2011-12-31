from django.test import TestCase
import hashlib
import uuid
from django.contrib.auth.models import User
from issuetracker.models import Issue, CaseEvent
from clinical_core.clinical_shared.utils import generator
from issuetracker import constants
from django.core.management import call_command
from permissions.models import Actor, PrincipalRoleRelation, Role
from tenant.models import Tenant


INITIAL_DESCRIPTION = "this is a case made by the test case"
CHANGED_DESCRIPTION = 'i just changed it, foo'


def create_user(username='mockuser', password='mockmock'):
    user = User()
    user.username = username
    # here, we mimic what the django auth system does
    # only we specify the salt to be 12345
    salt = '12345'
    hashed_pass = hashlib.sha1(salt+password).hexdigest()
    user.password = 'sha1$%s$%s' % (salt, hashed_pass)

    user.set_password(password)
    user.save()
    return user


class EventActivityVerificationTest(TestCase):
    fixtures = []

    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        Tenant.objects.all().delete()
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


    def testCreateIssueView(self, description = INITIAL_DESCRIPTION):
        #self.assertFalse(True)
        pass


    def testCreateIssueApi(self, description=INITIAL_DESCRIPTION):
        ###########################
        #get the basic counts
        user1 = generator.get_or_create_user()
        user2 = generator.get_or_create_user()

        actor_caregiver = generator.generate_actor(self.tenant, user1, 'caregiver')
        actor_provider = generator.generate_actor(self.tenant, user2, 'provider')

        oldcasecount = Issue.objects.all().count()
        oldevents = CaseEvent.objects.all().count()

#        newcase = Issue()
#        newcase.description = description
#        newcase.opened_by = role1
#        newcase.last_edit_by = role1
#
#        newcase.assigned_date = datetime.utcnow()
#        newcase.assigned_to = role2
#        newcase.category = Category.objects.all()[0]
#        newcase.status = Status.objects.all().filter(state_class=constants.CASE_STATE_OPEN)[0]
#        newcase.priority = Priority.objects.all()[0]
#        activity = ActivityClass.objects.filter(event_class=constants.CASE_EVENT_OPEN)[0]
#        newcase.save(activity=activity)

        newcase = Issue.objects.new_issue(constants.CATEGORY_CHOICES[0][0],
                              actor_caregiver.django_actor,
                              description,
                              "mock body %s" % (uuid.uuid4().hex),
                              constants.PRIORITY_MEDIUM,
                              status=constants.CASE_STATE_OPEN,
                              activity=constants.CASE_EVENT_OPEN
                              )

        #is the thing created?
        self.assertEqual(Issue.objects.all().count(), oldcasecount + 1)
        self.assertEqual(CaseEvent.objects.all().count(), oldevents + 1)
        #verify that the case count created has created a new caseevent
        events = CaseEvent.objects.filter(case=newcase)
        self.assertEqual(1,events.count())
        #verify that said case count is a new case event of type "open"
        self.assertEqual(constants.CASE_EVENT_OPEN, events[0].activity)
        return newcase

    def testCaseModifyClient(self, description = "A test case that modifies a case via the webUI using the web client."):
        #self.assertFalse(True)
        pass


    def testCaseModifyDescriptionApi(self):
        desc= uuid.uuid4().hex
        self.testCreateIssueApi(description=desc)

        user1 = generator.get_or_create_user()
        actor_provider_doc = generator.generate_actor(self.tenant, user1, 'provider')


        case = Issue.objects.all().get(description=desc)
        case.description = CHANGED_DESCRIPTION
        case.last_edit_by = actor_provider_doc.django_actor
        activity = constants.CASE_EVENT_EDIT
        case.save_comment="editing in testCaseModifyDescription"
        case.save(activity=activity)


        events = CaseEvent.objects.filter(case=case)
        #we just did an edit, so it should be 2
        self.assertEqual(2, events.count())

        #the top one due to the sort ordering should be the one we just did
        self.assertEqual(constants.CASE_EVENT_EDIT, events[0].activity)


        #quickly verify that the original description is still unchanged
        dbcase = Issue.objects.all().get(description=CHANGED_DESCRIPTION)
        self.assertEqual(dbcase.id, case.id)


    def testCaseCreateChildCases(self):
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
            activity = constants.CASE_EVENT_EDIT
            subissue.save_comment="editing in testCaseCreateChildCases"
            subissue.save(activity=activity)


        self.assertEqual(root_issue.child_issues.count(), CHILD_ISSUES)






