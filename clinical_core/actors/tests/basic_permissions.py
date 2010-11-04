from django.test import TestCase
from django.contrib.auth.models import User
from clinical_core.actors.models import Role, Actor, PatientActorLink, TriageNurse, Doctor, Caregiver
from clinical_core.patient.models import Patient

from clinical_core.clincore import generator as bootstrap
    
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
        Role.objects.all().delete()
        Actor.objects.all().delete()
        PatientActorLink.objects.all().delete()
        Patient.objects.all().delete()
        #print "Doctors:"  + str(Doctor.objects.all().count())        
        
    
    def testCreateSingleCareTeam(self):        
        print "===========================\nCreating singular patient with careteam"
        pt, caregivers, providers = bootstrap.generate_patient_and_careteam()
        print "created careteam for one patient"
        for cg in caregivers:
            self.assertEqual(cg.patients[0], pt)
            self.assertTrue(Actor.permissions.can_view(pt, cg.user))
        for prov in providers:
            self.assertEqual(prov.patients[0], pt)
            self.assertTrue(Actor.permissions.can_view(pt, prov.user))
        
    def testCreateMultipleSingleCareTeams(self):
        print "===============\nCreating multiple singular patient careteams"
        patients = []
        caregivers_list = {}
        providers_list = {}
        
        for num in range(0,MAX_MULTI_PATIENTS):
            pt, caregivers, providers = bootstrap.generate_patient_and_careteam()
            patients.append(pt)
            caregivers_list[pt] = caregivers
            providers_list[pt] = providers
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


    def testAdvancedPermissionsOnePatient(self):
        """
        Create a multitude of patients where a provider has varying actor roles (provider, none, etc)
        """
        patient = bootstrap.generate_patient()
        role_possibilities = ['caregiver', 'provider', None]
        for r in role_possibilities:
            user = self._createUser()
            if r != None:
                actor = bootstrap.generate_actor(user, r)
                pal = PatientActorLink(patient=patient, actor=actor, active=True)
                pal.save()
            

            if r == 'caregiver':                
                self.assertEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
            elif r == 'provider':
                self.assertNotEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
            elif r == None:
                self.assertEqual(Actor.permissions.get_roles(patient, user).count(), 0)

    def testAdvancedPermissionsThreePatients(self):
        """
        Create a multitude of patients where a provider has varying actor roles (provider, none, etc)
        """
        patients = []
        for i in range(0,3):
            patients.append(bootstrap.generate_patient())
            
            
        role_possibilities = ['caregiver', 'provider', None]
        user = self._createUser()
        for i in range(0,3):
            r = role_possibilities[i]
            patient = patients[i]
            if r != None:
                actor = bootstrap.generate_actor(user, r)
                pal = PatientActorLink(patient=patient, actor=actor, active=True)
                pal.save()
                

        for i in range(0,3):
            patient = patients[i]
            if i == 0: #caregiver
                self.assertEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
            elif i == 1: #provider:
                self.assertNotEqual(Actor.permissions.get_roles(patient, user)[0].role_type.model_class(), Caregiver)
                role_type = Actor.permissions.get_roles(patient, user)[0].role_type.model_class()
                if role_type == Doctor or role_type == TriageNurse:
                    pass
                else:
                    self.fail("Not a known role type")
            if i == 2:
                self.assertEqual(Actor.permissions.get_roles(patient, user).count(), 0)
            
    
        
    pass
