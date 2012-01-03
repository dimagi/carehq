import pdb
import random
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from actorpermission.models.actortypes import CaregiverActor, ProviderActor, CHWActor
from carehq_core import carehq_api
from clinical_shared.utils import generator
from clinical_shared.utils.scrambler import raddress
from permissions.models import PrincipalRoleRelation, Role, Actor
from tenant.models import Tenant

class CareHQClinicalTestCase(TestCase):
    """
    Basic test case with bootstrap bits for basic carehq environment setup within a test suite.
    """
    def _superSetup(self):
        #the setUp method cannot be called via super(), so need to call it explicitly as a parent class method
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        Tenant.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        call_command('carehq_init')
        self.tenant = Tenant.objects.all()[0]


    def setUp(self):
        self._superSetup()


    def _createUser(self):
        """
        The central user of this test Case
        """
        usr = User()
        usr.username = 'mockmock@mockmock.com'
        usr.set_password('mockmock')
        usr.first_name='mocky'
        usr.last_name = 'mock'
        usr.save()
        self.user=usr


    def _new_chw(self, tenant, user):
        chw_actor = CHWActor()
        chw_actor.first_name = user.first_name
        chw_actor.last_name = user.last_name
        chw_actor.title = "Mock CHW"
        chw_actor.phone_number = generator.random_number()
        chw_actor.save(tenant, user=user)
        self.assertTrue(carehq_api.add_chw(chw_actor))
        return chw_actor


    def _new_provider(self, tenant, user):
        provider_actor = ProviderActor()
        provider_actor.provider_title = generator.random_word(length=12)
        provider_actor.email = "%s@%s.com" % (generator.random_word(length=8), generator.random_word(length=8))
        provider_actor.facility_name = generator.random_word(length=12)
        provider_actor.facility_address = generator.random_text(length=12)
        provider_actor.save(tenant, user=user)
        self.assertTrue(carehq_api.add_provider(provider_actor))
        return provider_actor

    def _new_caregiver(self, tenant, user):
        caregiver_actor = CaregiverActor()
        caregiver_actor.phone_number = str(generator.random_number(length=11))
        caregiver_actor.relation = random.choice(CaregiverActor.RELATIONSHIP_CHOICES)[0]
        caregiver_actor.address = raddress()
        caregiver_actor.save(tenant, user=user)
        return caregiver_actor
