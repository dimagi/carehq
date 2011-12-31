from speechd.client import Priority
from django.test import TestCase
from django.contrib.auth.models import User
import random
from issuetracker import constants
import uuid
from django.core.management import  call_command
from issuetracker.models.issuecore import Issue
from patient.models.patientmodels import Patient
from permissions.models import Actor

MAX_MULTI_PATIENTS = 10


class CasePermissionsTest(TestCase):
    fixtures = ['samplesetup-fixture.json']
    def _createUser(self):
        usr = User()
        usr.username = "TestUser%d" % (User.objects.all().count())
        usr.first_name = "TestUser"
        usr.first_name = "Test%d" % (User.objects.all().count())
        usr.set_password("testtest")
        usr.save()
        return usr

    def setUp(self):
        #print "Doctors:"  + str(Doctor.objects.all().count())
        call_command('load_categories')
        User.objects.all().delete()
        Issue.objects.all().delete()
        Actor.objects.all().delete()
        Actor.objects.all().delete()
        Patient.objects.all().delete()
        #print "Doctors:"  + str(Doctor.objects.all().count())


    def _create_case(self, actor, description=None, priority=None):
        if priority == None:
            priority=Priority.objects.all()[0]
        if description == None:
            description = "mock body %s" % (uuid.uuid4().hex),

        newcase = Issue.objects.new_issue(Category.objects.all()[0],
                              actor,
                              description,
                              'some body',
                              priority,
                              status=Status.objects.all().filter(state_class=constants.CASE_STATE_OPEN)[0],
                              activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_OPEN)[0]
                              )
        return newcase


    def testCaseManager(self):
        pt1, cgs1, prov1 = generator.generate_patient_and_careteam()
        pt2, cgs2, prov2 = generator.generate_patient_and_careteam()
        actor_creator = generator.generate_actor(generator.get_or_create_user(), "provider")
        actor_editor1 = generator.generate_actor(generator.get_or_create_user(), "provider")
        actor_editor2 = generator.generate_actor(generator.get_or_create_user(), "provider")
        actor_closer = generator.generate_actor(generator.get_or_create_user(), "provider")

        total_cases = 12
        for i in range(total_cases):
            case = self._create_case(actor_creator, uuid.uuid4().hex)
            case.patient = pt1
            if i%2 == 0:
                case.last_edit_by = actor_editor1
            else:
                case.last_edit_by = actor_editor2
            case.description = "edited, foolio: " + str(uuid.uuid4().hex)
            activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_EDIT)[0]
            case.save(activity=activity)

        self.assertEqual(total_cases, Issue.objects.get_authored(actor_creator).count())
        self.assertEqual(0, Issue.objects.get_authored(actor_creator, patient=pt2).count())

        self.assertEqual(total_cases/2, Issue.objects.get_edited(actor_editor1).count())
        self.assertEqual(total_cases/2, Issue.objects.get_edited(actor_editor2).count())

        self.assertEqual(total_cases/2, Issue.objects.get_edited(actor_editor1, patient=pt1).count())
        self.assertEqual(0, Issue.objects.get_edited(actor_editor1, patient=pt2).count())

        self.assertEqual(total_cases/2, Issue.objects.get_edited(actor_editor2, patient=pt1).count())
        self.assertEqual(0, Issue.objects.get_edited(actor_editor2, patient=pt2).count())


    def testDisparateCases(self):
        """Create two patients and make disparate case sets and verify there's no spillage in the API calls.
        """
        pt1, cgs1, prov1 = generator.generate_patient_and_careteam()
        pt2, cgs2, prov2 = generator.generate_patient_and_careteam()

        num_case1 = random.randint(1,10)
        num_case2 = random.randint(1,10)
        total_cases = num_case1 + num_case2

        case1 = []
        case2 = []


        for i in range(num_case1):
            actor = prov1[0]
            case = self._create_case(actor, uuid.uuid4().hex)
            case.patient = pt1
            activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_EDIT)[0]
            case.save(activity=activity)
            case1.append(case)

        for i in range(num_case2):
            actor = prov2[0]
            case = self._create_case(actor, uuid.uuid4().hex)
            case.patient = pt2
            activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_EDIT)[0]
            case.save(activity=activity)
            case2.append(case)


        print "verifying case creation 1:"
        self.assertEqual(num_case1, Issue.objects.all().filter(patient=pt1).count())
        self.assertEqual(num_case1, pt1.cases.count())


        print "verifying case creation 2"
        self.assertEqual(num_case2, Issue.objects.all().filter(patient=pt2).count())
        self.assertEqual(num_case2, pt2.cases.count())





