import pdb
import random
from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth.models import User
from carehq_core import carehq_api, carehq_constants
from carehqapp.scripts.demo.demo_careteams import DEMO_CARETEAMS
from clinical_core.clinical_shared.utils import generator
from patient.models import Patient
from permissions import utils
from permissions.models import Actor, PrincipalRoleRelation, Role
from tenant.models import Tenant


MAX_MULTI_PATIENTS = 10


class BasicPermissionsTest(TestCase):
    def _createActors(self):        
        pass
    def _createPatient(self):
        pt = Patient()
        pass
    
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
        User.objects.all().delete()
        Actor.objects.all().delete()
        Patient.objects.all().delete()
        Role.objects.all()
        PrincipalRoleRelation.objects.all()
        #self.tenant = Tenant.objects.get_or_create(name="foo_test")[0]
        call_command('carehq_init')
        self.tenant = Tenant.objects.get(name='PACT')
        #print "Doctors:"  + str(Doctor.objects.all().count())

    def testCreateSingleCareTeamManually(self):
        print "===========================\nCreating singular patient with careteam manually"
        pt, caregivers, providers = generator.generate_patient_and_careteam(self.tenant, team_dictionary=random.choice(DEMO_CARETEAMS))
        print "created careteam for one patient"
        for cg in caregivers:
            self.assertEqual(carehq_api.get_permissions(cg)[0].content.couchdoc._id, pt._id)
            self.assertTrue(utils.has_permission(self.tenant, cg.django_actor, carehq_constants.perm_patient_view))
            self.assertFalse(utils.has_permission(self.tenant, cg.django_actor, carehq_constants.perm_patient_edit))
        for prov in providers:
            self.assertEqual(carehq_api.get_permissions(prov)[0].content.couchdoc._id, pt._id)
            self.assertTrue(utils.has_permission(self.tenant, prov.django_actor, carehq_constants.perm_patient_view))
            self.assertTrue(utils.has_permission(self.tenant, prov.django_actor, carehq_constants.perm_patient_edit))

    def testCreateSingleCareTeamAPI(self):
        print "===========================\nCreating singular patient with careteam via API"
        pt = generator.get_or_create_patient(self.tenant)

        for x in range(0,3):
            prov_actor = generator.generate_actor(self.tenant, generator.get_or_create_user(), 'provider')
            carehq_api.add_to_careteam(pt, prov_actor, Role.objects.get(name=carehq_constants.role_provider))
        for x in range(0,2):
            cg_actor = generator.generate_actor(self.tenant, generator.get_or_create_user(), 'caregiver')
            carehq_api.add_to_careteam(pt, cg_actor, Role.objects.get(name=carehq_constants.role_caregiver))

        #next, verify single careteam exists via the patient access API.
        cg_pull = carehq_api.get_patient_caregivers(pt)
        prov_pull = carehq_api.get_patient_providers(pt)

        self.assertEqual(2, cg_pull.count())
        self.assertEqual(3, prov_pull.count())

    def testCreateMultipleSingleCareTeams(self):
        """
        Generate Single patient careteams where providers have no overlap.
        """
        patients = []
        caregivers_list = {}
        providers_list = {}
        
        for careteam_dict in DEMO_CARETEAMS[0:6]: #these are the careteams with no overlap of providers and caregivers
            pt, caregivers, providers = generator.generate_patient_and_careteam(self.tenant, team_dictionary=careteam_dict)
        print "finished generating disparate patient careteams"
        
        #step 1: verify that that for each patient generated, ONLY the providers can view it
        for patient in patients:        
            print "check disparate networks for patient %s" % (patient)
            cg_subset = []
            prov_subset = []

            for pt2 in patients:
                if pt2 == patient:
                    continue
                cg_subset.append(caregivers_list[pt2])
                prov_subset.append(providers_list[pt2])
            
            for cgs in cg_subset:
                for cg in cgs:
                    self.assertNotEqual(cg.patients[0], patient)
                    self.assertFalse(Actor.permissions.can_view(patient, cg.user))
                
            for provs in prov_subset:
                for prov in provs:
                    self.assertNotEqual(prov.patients[0], patient)
                    self.assertFalse(Actor.permissions.can_view(patient, prov.user))


#    def testAdvancedPermissionsOnePatient(self):
#        """
#        Create a multitude of patients where a provider has varying roles (provider, none, etc)
#        """
#        patient = generator.get_or_create_patient(self.tenant)
#        role_possibilities = ['caregiver', 'provider', None]
#        for r in role_possibilities:
#            user = self._createUser()
#            if r != None:
#                pdb.set_trace()
#                actor = generator.generate_actor(self.tenant, r, user=user)
#
#            if r == 'caregiver':
#                self.assertEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
#            elif r == 'provider':
#                self.assertNotEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
#            elif r == None:
#                self.assertEqual(Actor.permissions.get_roles(patient, user).count(), 0)

#    def testAdvancedPermissionsThreePatients(self):
#        """
#        Create a multitude of patients where a provider has varying actor roles (provider, none, etc)
#        """
#        patients = []
#        for i in range(3):
#            patients.append(generator.get_or_create_patient(self.tenant))
#
#        role_options = ['caregiver', 'provider', None]
#        user = self._createUser()
#        for i in range(3):
#            patient = patients[i]
#            role = role_options[i]
#            if role != None:
#                actor = generator.generate_actor(self.tenant, user, role)
#                patient.add_actor(actor)
#
#        for i in range(0,3):
#            patient = patients[i]
#            if i == 0: #caregiver
#                self.assertEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
#            elif i == 1: #provider:
#                self.assertNotEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
#                role_type = Actor.permissions.get_roles(patient, user)[0].role_type.model_class()
#                if role_type == Doctor or role_type == TriageNurse:
#                    pass
#                else:
#                    self.fail("Not a known role type")
#            if i == 2:
#                self.assertEqual(Actor.permissions.get_roles(patient, user).count(), 0)
#
#
#    def testBusyProvider(self):
#        """Create a single provider/user caring for many patients."""
#        num_patients = 20
#        my_patients = 5
#
#        user = generator.get_or_create_user()
#        actor = generator.generate_actor(self.tenant, user, 'provider')
#
#        patients = [generator.get_or_create_patient(self.tenant) for i in range(num_patients)]
#        for i in range(my_patients):
#            patients[i].add_actor(actor)
